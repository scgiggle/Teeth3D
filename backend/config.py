import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Redis 配置
    REDIS_HOST: str = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT: int = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB: int = int(os.getenv('REDIS_DB', 0))
    
    # JWT 配置
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'your-secret-key-here-change-in-production')
    ALGORITHM: str = os.getenv('ALGORITHM', 'HS256')
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', 30))
    
    # 验证码配置
    CAPTCHA_EXPIRE_MINUTES: int = int(os.getenv('CAPTCHA_EXPIRE_MINUTES', 5))

    # MySQL 配置
    MYSQL_HOST: str = os.getenv('MYSQL_HOST', '127.0.0.1')
    MYSQL_PORT: int = int(os.getenv('MYSQL_PORT', 3306))
    MYSQL_USER: str = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD: str = os.getenv('MYSQL_PASSWORD', '123456')
    MYSQL_DB: str = os.getenv('MYSQL_DB', 'teethdreamer')

    #MongoDB 配置
    MONGO_HOST: str = os.getenv('MONGO_HOST', 'localhost')
    MONGO_PORT: int = int(os.getenv('MONGO_PORT', 27017))
    MONGO_DB: str = os.getenv('MONGO_DB', 'teeth3d_db')
    @property
    def DATABASE_URL(self) -> str:
        return (
            f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}"
            f"?charset=utf8mb4"
        )
    
    @property
    def MONGO_URL(self) -> str:
        return f"mongodb://{self.MONGO_HOST}:{self.MONGO_PORT}/{self.MONGO_DB}"
    
settings = Settings()
