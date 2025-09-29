# FastAPI 后端服务

这是一个基于 FastAPI 的 3D 重建和图像分割后端服务，包含用户认证、验证码、图像处理等功能。

## 功能特性

- ✅ 用户注册和登录
- ✅ 真实验证码生成和验证
- ✅ JWT 令牌认证
- ✅ 图像上传和分割
- ✅ 3D 模型重建
- ✅ Redis 数据存储
- ✅ CORS 跨域支持

## 技术栈

- **FastAPI**: 现代、快速的 Web 框架
- **Redis**: 数据存储和缓存
- **PIL (Pillow)**: 图像处理和验证码生成
- **JWT**: 用户认证
- **bcrypt**: 密码加密
- **Pydantic**: 数据验证

## 安装和运行

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 安装 Redis

**Windows:**
```bash
# 使用 Chocolatey
choco install redis-64

# 或下载 Redis for Windows
# https://github.com/microsoftarchive/redis/releases
```

**macOS:**
```bash
brew install redis
```

**Linux:**
```bash
sudo apt-get install redis-server
```

### 3. 启动 Redis

```bash
redis-server
```

### 4. 配置环境变量

创建 `.env` 文件（可选，有默认值）：

```env
# Redis 配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# JWT 配置
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 验证码配置
CAPTCHA_EXPIRE_MINUTES=5

# 服务器配置
HOST=0.0.0.0
PORT=8000
RELOAD=true
```

### 5. 启动服务

```bash
# 方式1: 使用启动脚本
python start.py

# 方式2: 直接使用 uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## API 文档

启动服务后，访问以下地址查看 API 文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API 接口

### 认证相关

- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `GET /api/auth/me` - 获取当前用户信息

### 验证码相关

- `GET /api/captcha` - 获取验证码
- `POST /api/captcha/verify` - 验证验证码

### 图像分割相关

- `POST /api/segmentation/upload` - 上传图像
- `GET /api/segmentation/{image_id}` - 获取分割结果
- `POST /api/segmentation/{image_id}/reconstruct` - 请求3D重建

### 3D模型相关

- `GET /api/model/{model_id}` - 获取3D模型信息

## 项目结构

```
backend/
├── main.py              # 主应用文件
├── config.py            # 配置管理
├── database.py          # 数据库连接
├── start.py             # 启动脚本
├── requirements.txt     # 依赖包
├── routers/             # 路由模块
│   ├── __init__.py
│   ├── auth.py          # 认证路由
│   ├── captcha.py       # 验证码路由
│   ├── segmentation.py  # 图像分割路由
│   └── models.py        # 3D模型路由
└── README.md           # 说明文档
```

## 开发说明

### 验证码实现

- 使用 PIL 生成随机验证码图片
- 验证码存储在 Redis 中，设置过期时间
- 支持点击刷新验证码

### 用户认证

- 使用 JWT 令牌进行身份验证
- 密码使用 bcrypt 加密存储
- 支持令牌过期和自动刷新

### 数据存储

- 使用 Redis 作为主要数据存储
- 支持用户信息、验证码、图像元数据等存储
- 自动过期机制

## 故障排除

### 常见问题

1. **Redis 连接失败**
   - 确保 Redis 服务正在运行
   - 检查 Redis 配置和端口

2. **验证码生成失败**
   - 检查 PIL 库是否正确安装
   - 确保系统有可用的字体文件

3. **CORS 错误**
   - 检查前端地址是否在 CORS 允许列表中
   - 确认前端和后端端口配置

### 日志查看

启动时添加 `--log-level debug` 参数查看详细日志：

```bash
uvicorn main:app --log-level debug
```

## 生产部署

### 使用 Gunicorn

```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 使用 Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 许可证

MIT License
