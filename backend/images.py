"""
图片处理路由模块
功能：裁剪到 4:3 (2677x2008)，文件名以 _0 或 _1 结尾的自动垂直镜像
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from PIL import Image
from typing import List, Optional
import io
import zipfile

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


def process_single_image(file_bytes: bytes, filename: str, 
                          manual_crop: Optional[dict] = None) -> bytes:
    """
    处理单张图片
    
    Args:
        file_bytes: 图片二进制数据
        filename: 文件名（用于判断是否需要镜像）
        manual_crop: 手动裁剪参数 {left, top, width, height}，如果为 None 则自动居中裁剪
    
    Returns:
        处理后的图片二进制数据
    """
    img = Image.open(io.BytesIO(file_bytes))
    
    # 确保是 RGB 模式
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # 裁剪
    if manual_crop:
        # 手动裁剪
        left = manual_crop.get('left', 0)
        top = manual_crop.get('top', 0)
        width = manual_crop.get('width', TARGET_WIDTH)
        height = manual_crop.get('height', TARGET_HEIGHT)
        img = img.crop((left, top, left + width, top + height))
        # 缩放到目标尺寸
        img = img.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
    else:
        # 自动居中裁剪
        img = crop_image(img)
    
    # 根据文件名判断是否需要镜像
    if needs_mirror(filename):
        img = mirror_image(img)
    
    # 输出为 JPEG
    output = io.BytesIO()
    img.save(output, format='JPEG', quality=95)
    output.seek(0)
    return output.getvalue()


@router.post("/process")
async def process_image(
    file: UploadFile = File(...),
    crop_left: Optional[int] = Form(None),
    crop_top: Optional[int] = Form(None),
    crop_width: Optional[int] = Form(None),
    crop_height: Optional[int] = Form(None),
):
    """
    处理单张图片
    
    - 自动裁剪到 4:3 (2677x2008)
    - 文件名以 _0 或 _1 结尾时自动垂直镜像
    - 可选：传入 crop_* 参数进行手动裁剪
    """
    try:
        file_bytes = await file.read()
        
        # 构建手动裁剪参数
        manual_crop = None
        if crop_left is not None and crop_top is not None:
            manual_crop = {
                'left': crop_left,
                'top': crop_top,
                'width': crop_width or TARGET_WIDTH,
                'height': crop_height or TARGET_HEIGHT,
            }
        
        processed = process_single_image(file_bytes, file.filename, manual_crop)
        
        return StreamingResponse(
            io.BytesIO(processed),
            media_type="image/jpeg",
            headers={
                "Content-Disposition": f"attachment; filename={file.filename}"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"图片处理失败: {str(e)}")


@router.post("/process-batch")
async def process_batch(files: List[UploadFile] = File(...)):
    """
    批量处理图片，返回 ZIP 压缩包
    
    - 所有图片自动裁剪到 4:3 (2677x2008)
    - 文件名以 _0 或 _1 结尾时自动垂直镜像
    """
    if not files:
        raise HTTPException(status_code=400, detail="请上传至少一张图片")
    
    try:
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file in files:
                file_bytes = await file.read()
                processed = process_single_image(file_bytes, file.filename)
                zf.writestr(file.filename, processed)
        
        zip_buffer.seek(0)
        
        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={
                "Content-Disposition": "attachment; filename=processed_images.zip"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量处理失败: {str(e)}")


@router.get("/config")
async def get_config():
    """获取处理配置（目标尺寸）"""
    return {
        "target_width": TARGET_WIDTH,
        "target_height": TARGET_HEIGHT,
        "aspect_ratio": "4:3"
    }
