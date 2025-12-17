"""
图片处理路由模块
功能：裁剪到 4:3 (2677x2008)，文件名以 _0 或 _1 结尾的自动垂直镜像
新增：历史记录持久化存储 (MySQL + MongoDB GridFS)
新增：批次分组、缩略图、批次下载
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import StreamingResponse
from PIL import Image
from typing import List, Optional
import io
import zipfile
import uuid
from datetime import datetime
from sqlalchemy import Integer, String, DateTime, ForeignKey, desc, func
from sqlalchemy.orm import Mapped, mapped_column, Session
from bson import ObjectId

from database import Base, get_db, get_mongo_fs
from routers.auth import get_current_user, get_current_user_from_query, User

# ---------------------- 数据库模型 ----------------------

class ProcessedImageORM(Base):
    __tablename__ = "processed_images"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True)
    batch_id: Mapped[str] = mapped_column(String(50), index=True, default="")  # 批次ID
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    original_file_id: Mapped[str] = mapped_column(String(50), nullable=False)  # MongoDB GridFS ID
    processed_file_id: Mapped[str] = mapped_column(String(50), nullable=False) # MongoDB GridFS ID
    thumbnail_file_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # 缩略图
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

# ---------------------- 业务逻辑 ----------------------

router = APIRouter()


# 配置常量
TARGET_WIDTH = 2677
TARGET_HEIGHT = 2008


def crop_image(img: Image.Image) -> Image.Image:
    """裁剪图片到指定尺寸 (4:3)，居中裁剪"""
    width, height = img.size
    
    # 计算居中裁剪区域
    left = (width - TARGET_WIDTH) // 2
    top = (height - TARGET_HEIGHT) // 2
    right = left + TARGET_WIDTH
    bottom = top + TARGET_HEIGHT
    
    # 如果图片小于目标尺寸，调整裁剪区域
    if width < TARGET_WIDTH or height < TARGET_HEIGHT:
        left = max(0, left)
        top = max(0, top)
        right = min(width, right)
        bottom = min(height, bottom)
    
    return img.crop((left, top, right, bottom))


def mirror_image(img: Image.Image) -> Image.Image:
    """垂直镜像图片（上下翻转）"""
    return img.transpose(Image.FLIP_TOP_BOTTOM)


def needs_mirror(filename: str) -> bool:
    """判断文件名是否需要镜像（以 _0 或 _1 结尾）"""
    import os
    name_no_ext = os.path.splitext(filename)[0]
    return name_no_ext.endswith('_0') or name_no_ext.endswith('_1')


def process_single_image_in_memory(file_bytes: bytes, filename: str, 
                          manual_crop: Optional[dict] = None) -> bytes:
    """内存中处理单张图片，返回 bytes"""
    img = Image.open(io.BytesIO(file_bytes))
    
    # 确保是 RGB 模式
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # 裁剪
    if manual_crop:
        left = manual_crop.get('left', 0)
        top = manual_crop.get('top', 0)
        width = manual_crop.get('width', TARGET_WIDTH)
        height = manual_crop.get('height', TARGET_HEIGHT)
        img = img.crop((left, top, left + width, top + height))
        img = img.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
    else:
        img = crop_image(img)
    
    # 镜像
    if needs_mirror(filename):
        img = mirror_image(img)
    
    output = io.BytesIO()
    img.save(output, format='JPEG', quality=95)
    output.seek(0)
    return output.getvalue()


def generate_thumbnail(img_bytes: bytes, max_size: int = 80) -> bytes:
    """
    生成缩略图
    
    Args:
        img_bytes: 图片二进制数据
        max_size: 缩略图最大边长（像素）
    
    Returns:
        缩略图的二进制数据
    """
    img = Image.open(io.BytesIO(img_bytes))
    
    # 确保是 RGB 模式
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # 按比例缩放，最大边不超过 max_size
    img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
    
    output = io.BytesIO()
    img.save(output, format='JPEG', quality=75)
    output.seek(0)
    return output.getvalue()


# ---------------------- 路由接口 ----------------------

@router.post("/process")
async def process_image(
    file: UploadFile = File(...),
    crop_left: Optional[int] = Form(None),
    crop_top: Optional[int] = Form(None),
    crop_width: Optional[int] = Form(None),
    crop_height: Optional[int] = Form(None),
    batch_id: Optional[str] = Form(None),  # 可选的批次ID，由前端传入
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    fs = Depends(get_mongo_fs)
):
    """
    处理单张图片并保存历史记录
    如果传入 batch_id，则使用该批次ID（用于前端分批上传但归属同一批次）
    """
    try:
        file_bytes = await file.read()
        
        # 使用传入的 batch_id，或者生成新的
        if not batch_id:
            batch_id = str(uuid.uuid4())[:8]
        
        # 1. 存原始图到 GridFS
        original_file_id = await fs.upload_from_stream(
            file.filename, 
            file_bytes, 
            metadata={"user_id": current_user.user_id, "type": "original", "batch_id": batch_id}
        )
        
        # 2. 处理图片
        manual_crop = None
        if crop_left is not None and crop_top is not None:
            manual_crop = {
                'left': crop_left,
                'top': crop_top,
                'width': crop_width or TARGET_WIDTH,
                'height': crop_height or TARGET_HEIGHT,
            }
        
        processed_bytes = process_single_image_in_memory(file_bytes, file.filename, manual_crop)
        
        # 3. 存处理后的图到 GridFS
        processed_filename = f"processed_{file.filename}"
        processed_file_id = await fs.upload_from_stream(
            processed_filename, 
            processed_bytes,
            metadata={"user_id": current_user.user_id, "type": "processed", "batch_id": batch_id}
        )
        
        # 4. 生成缩略图并存储
        thumbnail_bytes = generate_thumbnail(processed_bytes)
        thumbnail_file_id = await fs.upload_from_stream(
            f"thumb_{file.filename}",
            thumbnail_bytes,
            metadata={"user_id": current_user.user_id, "type": "thumbnail", "batch_id": batch_id}
        )
        
        # 5. 写入 MySQL 记录
        record = ProcessedImageORM(
            user_id=current_user.user_id,
            batch_id=batch_id,
            filename=file.filename,
            original_file_id=str(original_file_id),
            processed_file_id=str(processed_file_id),
            thumbnail_file_id=str(thumbnail_file_id),
            created_at=datetime.now()
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        
        return StreamingResponse(
            io.BytesIO(processed_bytes),
            media_type="image/jpeg",
            headers={
                "Content-Disposition": f"attachment; filename={file.filename}",
                "X-Image-Id": str(record.id),
                "X-Batch-Id": batch_id
            }
        )
    except Exception as e:
        print(f"Error processing image: {e}")
        raise HTTPException(status_code=500, detail=f"图片处理失败: {str(e)}")


@router.post("/process-batch")
async def process_batch(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    fs = Depends(get_mongo_fs)
):
    """
    批量处理图片，保存记录并返回 ZIP
    """
    if not files:
        raise HTTPException(status_code=400, detail="请上传至少一张图片")
    
    try:
        # 生成批次ID（这一批所有图片共享同一个 batch_id）
        batch_id = str(uuid.uuid4())[:8]
        
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file in files:
                file_bytes = await file.read()
                
                # 1. 存原始图
                original_file_id = await fs.upload_from_stream(
                    file.filename, 
                    file_bytes, 
                    metadata={"user_id": current_user.user_id, "type": "original", "batch_id": batch_id}
                )
                
                # 2. 处理
                processed_bytes = process_single_image_in_memory(file_bytes, file.filename)
                
                # 3. 存处理后的图
                processed_filename = f"processed_{file.filename}"
                processed_file_id = await fs.upload_from_stream(
                    processed_filename, 
                    processed_bytes,
                    metadata={"user_id": current_user.user_id, "type": "processed", "batch_id": batch_id}
                )
                
                # 4. 生成缩略图并存储
                thumbnail_bytes = generate_thumbnail(processed_bytes)
                thumbnail_file_id = await fs.upload_from_stream(
                    f"thumb_{file.filename}",
                    thumbnail_bytes,
                    metadata={"user_id": current_user.user_id, "type": "thumbnail", "batch_id": batch_id}
                )
                
                # 5. 记录
                record = ProcessedImageORM(
                    user_id=current_user.user_id,
                    batch_id=batch_id,
                    filename=file.filename,
                    original_file_id=str(original_file_id),
                    processed_file_id=str(processed_file_id),
                    thumbnail_file_id=str(thumbnail_file_id),
                    created_at=datetime.now()
                )
                db.add(record)
                
                zf.writestr(file.filename, processed_bytes)
            
            db.commit()
        
        zip_buffer.seek(0)
        
        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={
                "Content-Disposition": "attachment; filename=processed_images.zip",
                "X-Batch-Id": batch_id
            }
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"批量处理失败: {str(e)}")


@router.get("/history")
async def get_history(
    limit: int = 500,  # 增加默认限制到 500
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取历史处理记录，按批次分组返回
    
    返回格式:
    [
        {
            "batch_id": "xxx",
            "created_at": "2025-12-16 20:00:00",
            "count": 5,
            "images": [
                {"id": 1, "filename": "img1.png", "needs_mirror": true},
                ...
            ]
        }
    ]
    """
    records = db.query(ProcessedImageORM)\
        .filter(ProcessedImageORM.user_id == current_user.user_id)\
        .order_by(desc(ProcessedImageORM.created_at))\
        .limit(limit)\
        .all()
    
    # 按 batch_id 分组
    batches = {}
    for r in records:
        # 对于旧数据（没有 batch_id），使用记录 ID 作为唯一批次
        bid = r.batch_id if r.batch_id else f"legacy_{r.id}"
        
        if bid not in batches:
            batches[bid] = {
                "batch_id": bid,
                "created_at": r.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "images": []
            }
        
        batches[bid]["images"].append({
            "id": r.id,
            "filename": r.filename,
            "needs_mirror": needs_mirror(r.filename)
        })
    
    # 转为列表并添加 count
    result = list(batches.values())
    for batch in result:
        batch["count"] = len(batch["images"])
    
    return result


@router.get("/{image_id}/download")
async def download_history_image(
    image_id: int,
    type: str = "processed",  # processed or original
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    fs = Depends(get_mongo_fs)
):
    """下载历史图片"""
    record = db.query(ProcessedImageORM).filter(
        ProcessedImageORM.id == image_id,
        ProcessedImageORM.user_id == current_user.user_id
    ).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    
    file_id = record.processed_file_id if type == "processed" else record.original_file_id
    
    try:
        grid_out = await fs.open_download_stream(ObjectId(file_id))
        return StreamingResponse(
            grid_out,
            media_type="image/jpeg",
            headers={
                "Content-Disposition": f"attachment; filename={record.filename}"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail="文件未找到")


@router.delete("/{image_id}")
async def delete_history_image(
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    fs = Depends(get_mongo_fs)
):
    """删除历史记录"""
    record = db.query(ProcessedImageORM).filter(
        ProcessedImageORM.id == image_id,
        ProcessedImageORM.user_id == current_user.user_id
    ).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    
    # 尝试删除 GridFS 文件（不阻断）
    try:
        await fs.delete(ObjectId(record.original_file_id))
        await fs.delete(ObjectId(record.processed_file_id))
        if record.thumbnail_file_id:
            await fs.delete(ObjectId(record.thumbnail_file_id))
    except Exception as e:
        print(f"Delete GridFS error: {e}")
    
    db.delete(record)
    db.commit()
    
    return {"message": "删除成功"}


@router.get("/{image_id}/thumbnail")
async def get_thumbnail(
    image_id: int,
    token: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_query),
    fs = Depends(get_mongo_fs)
):
    """获取图片缩略图（如果不存在则动态生成）"""
    record = db.query(ProcessedImageORM).filter(
        ProcessedImageORM.id == image_id,
        ProcessedImageORM.user_id == current_user.user_id
    ).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    
    # 如果没有缩略图，动态生成并保存
    if not record.thumbnail_file_id:
        try:
            # 从 GridFS 读取处理后的图片
            grid_out = await fs.open_download_stream(ObjectId(record.processed_file_id))
            processed_bytes = await grid_out.read()
            
            # 生成缩略图
            thumbnail_bytes = generate_thumbnail(processed_bytes)
            
            # 保存缩略图到 GridFS
            thumbnail_file_id = await fs.upload_from_stream(
                f"thumb_{record.filename}",
                thumbnail_bytes,
                metadata={"user_id": current_user.user_id, "type": "thumbnail"}
            )
            
            # 更新数据库记录
            record.thumbnail_file_id = str(thumbnail_file_id)
            db.commit()
        except Exception as e:
            print(f"Generate thumbnail error: {e}")
            raise HTTPException(status_code=500, detail="缩略图生成失败")
    
    try:
        grid_out = await fs.open_download_stream(ObjectId(record.thumbnail_file_id))
        return StreamingResponse(
            grid_out,
            media_type="image/jpeg",
            headers={
                "Cache-Control": "max-age=86400"  # 缓存1天
            }
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail="缩略图文件未找到")


@router.get("/batch/{batch_id}/download")
async def download_batch(
    batch_id: str,
    token: Optional[str] = None,  # 支持 URL 直接下载
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_query),  # 使用 query 认证
    fs = Depends(get_mongo_fs)
):
    """下载整个批次的所有处理后图片（ZIP格式）"""
    records = db.query(ProcessedImageORM).filter(
        ProcessedImageORM.batch_id == batch_id,
        ProcessedImageORM.user_id == current_user.user_id
    ).all()
    
    if not records:
        raise HTTPException(status_code=404, detail="批次不存在")
    
    try:
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            for record in records:
                grid_out = await fs.open_download_stream(ObjectId(record.processed_file_id))
                file_data = await grid_out.read()
                zf.writestr(record.filename, file_data)
        
        zip_buffer.seek(0)
        
        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename=batch_{batch_id}.zip"
            }
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"下载失败: {str(e)}")


@router.delete("/batch/{batch_id}")
async def delete_batch(
    batch_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    fs = Depends(get_mongo_fs)
):
    """删除整个批次的所有图片"""
    records = db.query(ProcessedImageORM).filter(
        ProcessedImageORM.batch_id == batch_id,
        ProcessedImageORM.user_id == current_user.user_id
    ).all()
    
    if not records:
        raise HTTPException(status_code=404, detail="批次不存在")
    
    # 删除 GridFS 文件
    for record in records:
        try:
            await fs.delete(ObjectId(record.original_file_id))
            await fs.delete(ObjectId(record.processed_file_id))
            if record.thumbnail_file_id:
                await fs.delete(ObjectId(record.thumbnail_file_id))
        except Exception as e:
            print(f"Delete GridFS error: {e}")
    
    # 删除数据库记录
    for record in records:
        db.delete(record)
    db.commit()
    
    return {"message": f"已删除批次 {batch_id}，共 {len(records)} 张图片"}


@router.delete("/history/all")
async def delete_all_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    fs = Depends(get_mongo_fs)
):
    """删除当前用户的所有历史记录"""
    records = db.query(ProcessedImageORM).filter(
        ProcessedImageORM.user_id == current_user.user_id
    ).all()
    
    if not records:
        return {"message": "没有历史记录"}
    
    # 删除 GridFS 文件
    for record in records:
        try:
            await fs.delete(ObjectId(record.original_file_id))
            await fs.delete(ObjectId(record.processed_file_id))
            if record.thumbnail_file_id:
                await fs.delete(ObjectId(record.thumbnail_file_id))
        except Exception as e:
            print(f"Delete GridFS error: {e}")
    
    # 删除数据库记录
    count = len(records)
    for record in records:
        db.delete(record)
    db.commit()
    
    return {"message": f"已删除全部历史记录，共 {count} 张图片"}


@router.get("/config")
async def get_config():
    """获取处理配置"""
    return {
        "target_width": TARGET_WIDTH,
        "target_height": TARGET_HEIGHT,
        "aspect_ratio": "4:3"
    }
