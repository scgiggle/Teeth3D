from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import redis
import os
from dotenv import load_dotenv

from routers import auth, captcha, segmentation, models, project
from database import get_redis

load_dotenv()

# Redis 连接管理
redis_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时初始化 Redis 连接
    global redis_client
    redis_client = redis.Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', 6379)),
        db=int(os.getenv('REDIS_DB', 0)),
        decode_responses=True
    )

    # 尝试预加载 SAM2 模型（非阻塞启动，失败仅记录）
    try:
        # call function to initialize and cache model
        segmentation.get_sam2_model_and_predictor()
        print("SAM2 model preload attempted")
    except Exception as e:
        # 不阻塞启动，只记录，以便开发时查看原因
        print(f"Warning: SAM2 model preload failed: {e}")

    yield
    # 关闭时清理资源
    if redis_client:
        redis_client.close()

app = FastAPI(
    title="3D Reconstruction API",
    description="3D模型重建和图像分割API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ],  # 前端开发服务器
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 依赖注入：获取 Redis 客户端
async def get_redis_client():
    return redis_client

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(captcha.router, prefix="/api", tags=["验证码"])
app.include_router(segmentation.router, prefix="/api/segmentation", tags=["图像分割"])
app.include_router(models.router, prefix="/api/model", tags=["3D模型"])
app.include_router(project.router, prefix="/api/project", tags=["项目"])

@app.get("/")
async def root():
    return {"message": "3D Reconstruction API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
