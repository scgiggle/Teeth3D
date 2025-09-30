from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import redis
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from database import get_redis, get_db
from config import settings

router = APIRouter()
security = HTTPBearer()

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256", "bcrypt_sha256", "bcrypt"],
    default="pbkdf2_sha256",
    deprecated="auto",
)

class UserRegister(BaseModel):
    username: str
    password: str
    email: EmailStr
    captcha: str
    captcha_id: str

class UserLogin(BaseModel):
    username: str
    password: str
    captcha: str
    captcha_id: str

class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    username: str
    email: str
    user_id: int | None = None

# SQLAlchemy ORM for user table
from sqlalchemy import Integer, String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from database import Base

class UserORM(Base):
    __tablename__ = "user"
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    account: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    avatar: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    department: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    title: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    position: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    license_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_admin: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    status: Mapped[Optional[bool]] = mapped_column(Boolean, default=True)
    last_login: Mapped[Optional[DateTime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime)
    updated_at: Mapped[Optional[DateTime]] = mapped_column(DateTime)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """验证令牌"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

async def verify_captcha(captcha: str, captcha_id: str, redis_client: redis.Redis) -> bool:
    """验证验证码"""
    stored_captcha = redis_client.get(f"captcha:{captcha_id}")
    if not stored_captcha:
        return False
    return captcha.lower() == stored_captcha.lower()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    redis_client: redis.Redis = Depends(get_redis),
    db: Session = Depends(get_db)
) -> User:
    """获取当前用户"""
    if not redis_client:
        raise HTTPException(status_code=500, detail="Redis connection failed")
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = verify_token(credentials.credentials)
        if payload is None:
            raise credentials_exception
        
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # 从MySQL获取用户信息
    user_row = db.query(UserORM).filter(UserORM.account == username).first()
    if not user_row:
        raise credentials_exception
    return User(username=user_row.account, email=user_row.email or "", user_id=user_row.user_id)

@router.post("/register", response_model=dict)
async def register(
    user_data: UserRegister,
    redis_client: redis.Redis = Depends(get_redis),
    db: Session = Depends(get_db)
):
    """用户注册"""
    if not redis_client:
        raise HTTPException(status_code=500, detail="Redis connection failed")
    
    # 验证验证码
    if not await verify_captcha(user_data.captcha, user_data.captcha_id, redis_client):
        raise HTTPException(status_code=400, detail="验证码错误或已过期")
    
    try:
        # 检查用户名/邮箱是否已存在
        if db.query(UserORM).filter(UserORM.account == user_data.username).first():
            raise HTTPException(status_code=400, detail="用户名已存在")
        if user_data.email and db.query(UserORM).filter(UserORM.email == user_data.email).first():
            raise HTTPException(status_code=400, detail="邮箱已被注册")

        # 创建用户
        hashed_password = get_password_hash(user_data.password)
        row = UserORM(
            account=user_data.username,
            password=hashed_password,
            name=user_data.username,
            email=user_data.email,
            status=True,
        )
        db.add(row)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        # 将底层错误转为可读信息
        raise HTTPException(status_code=500, detail=f"数据库错误: {str(e)}")
    
    # 删除验证码
    redis_client.delete(f"captcha:{user_data.captcha_id}")
    
    return {"message": "注册成功"}

@router.post("/login", response_model=Token)
async def login(
    user_data: UserLogin,
    redis_client: redis.Redis = Depends(get_redis),
    db: Session = Depends(get_db)
):
    """用户登录"""
    if not redis_client:
        raise HTTPException(status_code=500, detail="Redis connection failed")
    
    # 验证验证码
    if not await verify_captcha(user_data.captcha, user_data.captcha_id, redis_client):
        raise HTTPException(status_code=400, detail="验证码错误或已过期")
    
    # 获取用户信息（MySQL）
    row = db.query(UserORM).filter(UserORM.account == user_data.username).first()
    if not row:
        raise HTTPException(status_code=400, detail="用户名或密码错误")

    if not verify_password(user_data.password, row.password):
        raise HTTPException(status_code=400, detail="用户名或密码错误")
    
    # 生成访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": row.account}, expires_delta=access_token_expires
    )
    
    # 删除验证码
    redis_client.delete(f"captcha:{user_data.captcha_id}")
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user
