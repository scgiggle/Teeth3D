from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import uuid
import redis
from typing import Optional

from database import get_redis
from routers.auth import get_current_user, User

router = APIRouter()

class SegmentationResult(BaseModel):
    image_id: str
    status: str
    result_url: Optional[str] = None

@router.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    redis_client: redis.Redis = Depends(get_redis)
):
    """上传图像进行分割"""
    if not redis_client:
        raise HTTPException(status_code=500, detail="Redis connection failed")
    
    # 验证文件类型
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="只支持图像文件")
    
    # 生成图像ID
    image_id = str(uuid.uuid4())
    
    # 这里应该保存文件到磁盘或云存储
    # 暂时只存储元数据
    image_info = {
        "image_id": image_id,
        "filename": file.filename,
        "content_type": file.content_type,
        "user": current_user.username,
        "status": "uploaded",
        "created_at": "2024-01-01T00:00:00"
    }
    
    redis_client.hset(f"image:{image_id}", mapping=image_info)
    
    return {"image_id": image_id, "message": "图像上传成功"}

@router.get("/{image_id}")
async def get_segmentation_result(
    image_id: str,
    current_user: User = Depends(get_current_user),
    redis_client: redis.Redis = Depends(get_redis)
):
    """获取分割结果"""
    if not redis_client:
        raise HTTPException(status_code=500, detail="Redis connection failed")
    
    image_info = redis_client.hgetall(f"image:{image_id}")
    if not image_info:
        raise HTTPException(status_code=404, detail="图像不存在")
    
    # 检查用户权限
    if image_info["user"] != current_user.username:
        raise HTTPException(status_code=403, detail="无权限访问")
    
    return SegmentationResult(
        image_id=image_id,
        status=image_info["status"],
        result_url=image_info.get("result_url")
    )

@router.post("/{image_id}/reconstruct")
async def request_reconstruction(
    image_id: str,
    current_user: User = Depends(get_current_user),
    redis_client: redis.Redis = Depends(get_redis)
):
    """请求3D重建"""
    if not redis_client:
        raise HTTPException(status_code=500, detail="Redis connection failed")
    
    image_info = redis_client.hgetall(f"image:{image_id}")
    if not image_info:
        raise HTTPException(status_code=404, detail="图像不存在")
    
    # 检查用户权限
    if image_info["user"] != current_user.username:
        raise HTTPException(status_code=403, detail="无权限访问")
    
    # 更新状态为重建中
    redis_client.hset(f"image:{image_id}", "status", "reconstructing")
    
    # 生成模型ID
    model_id = str(uuid.uuid4())
    redis_client.hset(f"model:{model_id}", mapping={
        "model_id": model_id,
        "image_id": image_id,
        "user": current_user.username,
        "status": "processing",
        "created_at": "2024-01-01T00:00:00"
    })
    
    return {"model_id": model_id, "message": "3D重建请求已提交"}
