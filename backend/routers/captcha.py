from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import redis
import random
import string
import base64
import io
from PIL import Image, ImageDraw, ImageFont
import uuid
from typing import Optional

from database import get_redis
from config import settings

router = APIRouter()

class CaptchaVerifyRequest(BaseModel):
    captcha: str
    captcha_id: str

class CaptchaResponse(BaseModel):
    captcha_id: str
    image: str

def generate_captcha_text(length: int = 4) -> str:
    """生成随机验证码文本"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def generate_captcha_image(text: str) -> Image.Image:
    """生成验证码图片"""
    # 创建图片
    width, height = 120, 50
    image = Image.new('RGB', (width, height), color=(240, 240, 240))
    draw = ImageDraw.Draw(image)
    
    # 绘制干扰线
    for _ in range(5):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        draw.line([(x1, y1), (x2, y2)], fill=color, width=1)
    
    # 绘制干扰点
    for _ in range(50):
        x = random.randint(0, width)
        y = random.randint(0, height)
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        draw.point((x, y), fill=color)
    
    # 绘制验证码文字
    try:
        # 尝试使用系统字体
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 20)
        except:
            font = ImageFont.load_default()
    
    for i, char in enumerate(text):
        x = 15 + i * 22
        y = 15 + random.randint(-5, 5)
        color = (random.randint(0, 100), random.randint(0, 100), random.randint(0, 100))
        # 添加文字旋转
        angle = random.randint(-15, 15)
        draw.text((x, y), char, font=font, fill=color)
    
    return image

@router.get("/captcha", response_model=CaptchaResponse)
async def get_captcha(redis_client: redis.Redis = Depends(get_redis)):
    """获取验证码"""
    if not redis_client:
        raise HTTPException(status_code=500, detail="Redis connection failed")
    
    # 生成验证码
    captcha_text = generate_captcha_text()
    captcha_id = str(uuid.uuid4())
    
    # 生成验证码图片
    image = generate_captcha_image(captcha_text)
    
    # 转换为base64
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    # 存储验证码到Redis，设置过期时间
    redis_client.setex(
        f"captcha:{captcha_id}", 
        settings.CAPTCHA_EXPIRE_MINUTES * 60, 
        captcha_text.lower()
    )
    
    return CaptchaResponse(
        captcha_id=captcha_id,
        image=f"data:image/png;base64,{img_str}"
    )

@router.post("/captcha/verify")
async def verify_captcha(
    request: CaptchaVerifyRequest,
    redis_client: redis.Redis = Depends(get_redis)
):
    """验证验证码"""
    if not redis_client:
        raise HTTPException(status_code=500, detail="Redis connection failed")
    
    # 从Redis获取存储的验证码
    stored_captcha = redis_client.get(f"captcha:{request.captcha_id}")
    
    if not stored_captcha:
        return {"valid": False, "message": "验证码已过期"}
    
    # 验证用户输入的验证码
    if request.captcha.lower() == stored_captcha.lower():
        # 验证成功后删除验证码
        redis_client.delete(f"captcha:{request.captcha_id}")
        return {"valid": True, "message": "验证码正确"}
    else:
        return {"valid": False, "message": "验证码错误"}
