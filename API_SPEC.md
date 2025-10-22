# 任务管理API接口规范

## 概述
此文档定义了牙齿3D重建任务管理系统的后端API接口规范，供前端调用。

## 基础信息
- 基础URL: `http://localhost:8000/api`
- 认证方式: JWT Bearer Token
- 数据格式: JSON

## 数据模型

### Task (任务对象)
```json
{
  "id": 1,
  "name": "患者张三 - 全口重建",
  "fileCount": 24,
  "startTime": "2025-10-22T14:30:00Z",
  "progress": 65,
  "status": "processing",
  "estimatedTime": "159分钟",
  "resultPath": "/results/task_1_result.obj",
  "stages": [
    {
      "name": "图像预处理",
      "status": "completed"
    },
    {
      "name": "特征提取", 
      "status": "completed"
    },
    {
      "name": "三维重建",
      "status": "processing"
    },
    {
      "name": "网格优化",
      "status": "pending"
    },
    {
      "name": "纹理映射",
      "status": "pending"
    },
    {
      "name": "后处理",
      "status": "pending"
    }
  ],
  "errorMessage": null,
  "createdAt": "2025-10-22T14:30:00Z",
  "updatedAt": "2025-10-22T15:30:00Z"
}
```

### 状态枚举
- `status`: `"processing"` | `"completed"` | `"failed"` | `"paused"`
- `stage.status`: `"pending"` | `"processing"` | `"completed"` | `"failed"`

## API 接口

### 1. 获取任务列表
```http
GET /api/tasks
```

**查询参数:**
- `page` (int, optional): 页码，默认1
- `pageSize` (int, optional): 每页数量，默认10
- `status` (string, optional): 过滤状态
- `userId` (int, optional): 用户ID过滤

**响应:**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "tasks": [Task],
    "total": 100,
    "page": 1,
    "pageSize": 10
  }
}
```

### 2. 获取任务进度
```http
GET /api/tasks/{taskId}/progress
```

**响应:**
```json
{
  "code": 200,
  "message": "success", 
  "data": {
    "id": 1,
    "progress": 65,
    "status": "processing",
    "currentStage": "三维重建",
    "estimatedTime": "159分钟",
    "stages": [StageObject]
  }
}
```

### 3. 创建新任务
```http
POST /api/tasks
```

**请求体:**
```json
{
  "name": "患者姓名 - 重建类型",
  "reconstructionType": "全口重建",
  "description": "任务描述",
  "imageIds": [1, 2, 3],
  "priority": 1
}
```

**响应:**
```json
{
  "code": 200,
  "message": "任务创建成功",
  "data": {
    "taskId": 123,
    "estimatedDuration": "2小时"
  }
}
```

### 4. 暂停任务
```http
POST /api/tasks/{taskId}/pause
```

**响应:**
```json
{
  "code": 200,
  "message": "任务已暂停",
  "data": {
    "taskId": 1,
    "status": "paused"
  }
}
```

### 5. 恢复任务
```http
POST /api/tasks/{taskId}/resume
```

**响应:**
```json
{
  "code": 200,
  "message": "任务已恢复",
  "data": {
    "taskId": 1,
    "status": "processing"
  }
}
```

### 6. 重试失败任务
```http
POST /api/tasks/{taskId}/retry
```

**响应:**
```json
{
  "code": 200,
  "message": "任务已重新开始",
  "data": {
    "taskId": 1,
    "status": "processing"
  }
}
```

### 7. 删除任务
```http
DELETE /api/tasks/{taskId}
```

**响应:**
```json
{
  "code": 200,
  "message": "任务已删除"
}
```

### 8. 下载任务结果
```http
GET /api/tasks/{taskId}/download
```

**响应:** 文件流 (Content-Type: application/octet-stream)

## 错误响应格式
```json
{
  "code": 400,
  "message": "错误描述",
  "detail": "详细错误信息"
}
```

## 常见错误码
- `400`: 请求参数错误
- `401`: 未认证或Token过期
- `403`: 权限不足
- `404`: 任务不存在
- `409`: 任务状态冲突（如已完成的任务无法暂停）
- `500`: 服务器内部错误

## 实时更新
对于进度更新，前端采用轮询方式，建议：
- 正在处理的任务：每5秒轮询一次
- 已完成/失败的任务：停止轮询
- 当页面不可见时暂停轮询以节省资源

## 数据库表结构建议

### tasks 表
```sql
CREATE TABLE tasks (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(200) NOT NULL,
  reconstruction_type ENUM('全口重建','单口重建','局部重建'),
  description TEXT,
  status ENUM('processing','completed','failed','paused') DEFAULT 'processing',
  progress TINYINT DEFAULT 0,
  current_stage VARCHAR(50),
  estimated_time VARCHAR(50),
  result_path VARCHAR(255),
  error_message TEXT,
  user_id BIGINT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  INDEX idx_user_id (user_id),
  INDEX idx_status (status),
  INDEX idx_created_at (created_at)
);
```

### task_stages 表
```sql
CREATE TABLE task_stages (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  task_id BIGINT NOT NULL,
  stage_name VARCHAR(50) NOT NULL,
  stage_order TINYINT NOT NULL,
  status ENUM('pending','processing','completed','failed') DEFAULT 'pending',
  started_at TIMESTAMP NULL,
  completed_at TIMESTAMP NULL,
  
  FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
  INDEX idx_task_id (task_id)
);
```

## 备注
- 所有时间字段使用ISO 8601格式 (YYYY-MM-DDTHH:mm:ssZ)
- 文件路径使用相对路径，便于部署时调整
- 进度值为0-100的整数
- 建议实现任务队列机制，避免同时处理过多任务导致资源耗尽