from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import Integer, String, Enum, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
import os
from datetime import datetime

from database import Base, get_db
from routers.auth import get_current_user, User


class ProjectORM(Base):
    __tablename__ = "project_data"
    project_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    reconstruction_type: Mapped[str] = mapped_column(String(20), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(10), default='重建中')
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    result_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    progress: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # tags/priority 忽略建模，避免方言差异


class ProjectImageORM(Base):
    __tablename__ = "project_images"
    image_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("project_data.project_id"), nullable=False)
    image_path: Mapped[str] = mapped_column(String(255), nullable=False)
    is_cover: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    uploaded_at: Mapped[Optional[datetime]] = mapped_column(DateTime)


class ProjectCreate(BaseModel):
    project_name: str
    reconstruction_type: str
    description: Optional[str] = None


router = APIRouter()


@router.get("/", response_model=dict)
def list_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = 20,
):
    rows = (
        db.query(ProjectORM)
        .filter(ProjectORM.user_id == current_user.user_id)
        .order_by(ProjectORM.created_at.desc())
        .limit(limit)
        .all()
    )
    items = [
        {
            "project_id": r.project_id,
            "project_name": r.project_name,
            "reconstruction_type": r.reconstruction_type,
            "status": r.status,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]
    return {"items": items}

@router.post("/", response_model=dict)
def create_project(
    payload: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 名称唯一性检查
    exists = db.query(ProjectORM).filter(ProjectORM.project_name == payload.project_name).first()
    if exists:
        raise HTTPException(status_code=400, detail="项目名称已存在")
    from zoneinfo import ZoneInfo
    now = datetime.now(ZoneInfo('Asia/Shanghai'))
    row = ProjectORM(
        project_name=payload.project_name,
        reconstruction_type=payload.reconstruction_type,
        description=payload.description,
        status='重建中',
        created_at=now,
        updated_at=now,
        user_id=current_user.user_id,
        progress=0,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return {"project_id": row.project_id, "status": row.status, "created_at": row.created_at.isoformat()}


@router.post("/{project_id}/images", response_model=dict)
def upload_project_image(
    project_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 校验项目存在且归属
    project = db.query(ProjectORM).filter(ProjectORM.project_id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    # 保存到磁盘
    uploads_dir = os.path.join(os.path.dirname(__file__), "..", "uploads", str(project_id))
    uploads_dir = os.path.abspath(uploads_dir)
    os.makedirs(uploads_dir, exist_ok=True)
    from zoneinfo import ZoneInfo
    now = datetime.now(ZoneInfo('Asia/Shanghai'))
    filename = f"{int(now.timestamp())}_{file.filename}"
    filepath = os.path.join(uploads_dir, filename)
    with open(filepath, 'wb') as f:
        f.write(file.file.read())

    rel_path = f"uploads/{project_id}/{filename}"
    # 第一张设为封面：若该项目还没有图片，则 is_cover=1，否则 0
    has_image = db.query(ProjectImageORM).filter(ProjectImageORM.project_id == project_id).first() is not None
    row = ProjectImageORM(
        project_id=project_id,
        image_path=rel_path,
        is_cover=0 if has_image else 1,
    uploaded_at=now
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return {"image_id": row.image_id, "image_path": rel_path}


