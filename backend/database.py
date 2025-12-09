import redis
import os
from typing import Optional
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase, scoped_session
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket
from config import settings

def get_redis() -> Optional[redis.Redis]:
    """获取 Redis 客户端"""
    try:
        client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            db=int(os.getenv('REDIS_DB', 0)),
            decode_responses=True
        )
        # 测试连接
        client.ping()
        return client
    except Exception as e:
        print(f"Redis connection error: {e}")
        return None

# SQLAlchemy 基础设施
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

@event.listens_for(engine, 'connect')
def set_timezone(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("SET time_zone='+8:00'")
    cursor.close()

SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 建立 MongoDB 连接
mongo_client = AsyncIOMotorClient(settings.MONGO_URL)
mongo_db = mongo_client[settings.MONGO_DB]

# 依赖注入函数 (用于 FastAPI 路由)
async def get_mongo_db():
    return mongo_db
async def get_mongo_fs():
    return AsyncIOMotorGridFSBucket(mongo_db)