#!/usr/bin/env python3
"""
FastAPI 后端启动脚本
"""
import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    # 从环境变量获取配置，或使用默认值
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("RELOAD", "true").lower() == "true"
    
    print(f"启动 FastAPI 服务器...")
    print(f"地址: http://{host}:{port}")
    print(f"API 文档: http://{host}:{port}/docs")
    print(f"重载模式: {reload}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
