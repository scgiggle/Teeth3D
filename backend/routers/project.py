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


class PatientORM(Base):
    __tablename__ = "patients"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    patient_id: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime)


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
    patient_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("patients.id"), nullable=True)
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
    project_name: str  # 前端传来的患者编号
    reconstruction_type: str
    description: Optional[str] = None


router = APIRouter()


@router.get("/patients", response_model=dict)
def list_patients(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取所有患者列表"""
    rows = db.query(PatientORM).order_by(PatientORM.created_at.desc()).all()
    items = [
        {
            "patient_id": r.patient_id,
            "name": r.name,
            "age": r.age,
            "gender": r.gender,
        }
        for r in rows
    ]
    return {"items": items}


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
    from zoneinfo import ZoneInfo
    now = datetime.now(ZoneInfo('Asia/Shanghai'))
    
    # payload.project_name 实际是患者编号
    patient_number = payload.project_name
    
    # 1. 查找或创建患者记录
    patient = db.query(PatientORM).filter(PatientORM.patient_id == patient_number).first()
    if not patient:
        patient = PatientORM(
            patient_id=patient_number,
            created_at=now,
            updated_at=now
        )
        db.add(patient)
        db.commit()
        db.refresh(patient)
    
    # 2. 生成项目名称：患者编号-1, 患者编号-2...
    counter = 1
    while True:
        project_name = f"{patient_number}-{counter}"
        exists = db.query(ProjectORM).filter(ProjectORM.project_name == project_name).first()
        if not exists:
            break
        counter += 1
    
    # 3. 创建项目记录
    row = ProjectORM(
        project_name=project_name,
        reconstruction_type=payload.reconstruction_type,
        description=payload.description,
        status='重建中',
        created_at=now,
        updated_at=now,
        user_id=current_user.user_id,
        patient_id=patient.id,
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
    # 校验项目存在且归属，如果不存在则报错
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


@router.delete("/{project_id}", response_model=dict)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 校验项目存在且归属当前用户
    project = db.query(ProjectORM).filter(
        ProjectORM.project_id == project_id,
        ProjectORM.user_id == current_user.user_id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在或无权限删除")
    
    # 删除关联的图片记录
    images = db.query(ProjectImageORM).filter(ProjectImageORM.project_id == project_id).all()
    
    # 删除磁盘上的图片文件
    import shutil
    uploads_dir = os.path.join(os.path.dirname(__file__), "..", "uploads", str(project_id))
    uploads_dir = os.path.abspath(uploads_dir)
    if os.path.exists(uploads_dir):
        try:
            shutil.rmtree(uploads_dir)
        except Exception as e:
            # 文件删除失败不阻断数据库删除
            print(f"Warning: Failed to delete files for project {project_id}: {e}")
    
    # 删除数据库记录
    for image in images:
        db.delete(image)
    
    db.delete(project)
    db.commit()
    
    return {"message": "项目删除成功", "project_id": project_id}


