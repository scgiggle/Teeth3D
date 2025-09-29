from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import redis
from typing import Optional

from database import get_redis
from routers.auth import get_current_user, User

router = APIRouter()

class ModelInfo(BaseModel):
    model_id: str
    image_id: str
    status: str
    model_url: Optional[str] = None
    created_at: str

    # 允许以 "model_" 开头的字段名，避免 Pydantic 命名空间告警
    model_config = {
        'protected_namespaces': ()
    }

@router.get("/{model_id}")
async def get_model(
    model_id: str,
    current_user: User = Depends(get_current_user),
    redis_client: redis.Redis = Depends(get_redis)
):
    """获取3D模型信息"""
    if not redis_client:
        raise HTTPException(status_code=500, detail="Redis connection failed")
    
    model_info = redis_client.hgetall(f"model:{model_id}")
    if not model_info:
        raise HTTPException(status_code=404, detail="模型不存在")
    
    # 检查用户权限
    if model_info["user"] != current_user.username:
        raise HTTPException(status_code=403, detail="无权限访问")
    
    return ModelInfo(
        model_id=model_id,
        image_id=model_info["image_id"],
        status=model_info["status"],
        model_url=model_info.get("model_url"),
        created_at=model_info["created_at"]
    )
