from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import Integer, String, Enum, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
from datetime import datetime, timedelta

from bson import ObjectId

from database import Base, get_db, get_mongo_fs
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
    finish_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    # tags/priority 忽略建模，避免方言差异


class ProjectImageORM(Base):
    __tablename__ = "project_images"
    image_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("project_data.project_id"), nullable=False)
    file_id: Mapped[str] = mapped_column(String(255), nullable=False)
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
    from zoneinfo import ZoneInfo
    now = datetime.now(ZoneInfo('Asia/Shanghai'))
    cutoff = now - timedelta(minutes=10)
    # 将超过10分钟仍为"重建中"的项目自动标记为"已完成"
    (db.query(ProjectORM)
       .filter(ProjectORM.user_id == current_user.user_id)
       .filter(ProjectORM.status != '已完成')
       .filter(ProjectORM.created_at <= cutoff)
       .update({ProjectORM.status: '已完成', ProjectORM.updated_at: now, ProjectORM.finish_time: now}, synchronize_session=False))
    db.commit()

    rows = (
        db.query(ProjectORM, PatientORM.patient_id)
        .outerjoin(PatientORM, ProjectORM.patient_id == PatientORM.id)
        .filter(ProjectORM.user_id == current_user.user_id)
        .order_by(ProjectORM.created_at.desc())
        .limit(limit)
        .all()
    )
    items = []
    for project, patient_number in rows:
        items.append(
            {
                "project_id": project.project_id,
                "project_name": project.project_name,
                "patient_number": patient_number,
                "reconstruction_type": project.reconstruction_type,
                "status": project.status,
                "created_at": project.created_at.isoformat() if project.created_at else None,
                "finish_time": project.finish_time.isoformat() if project.finish_time else None,
            }
        )
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
    return {
        "project_id": row.project_id,
        "project_name": row.project_name,
        "patient_number": patient_number,
        "status": row.status,
        "created_at": row.created_at.isoformat(),
    }


@router.post("/{project_id}/images", response_model=dict)
async def upload_project_image(
    project_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    fs = Depends(get_mongo_fs),
):
    # 校验项目存在且归属，如果不存在则报错
    project = db.query(ProjectORM).filter(ProjectORM.project_id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    from zoneinfo import ZoneInfo
    now = datetime.now(ZoneInfo('Asia/Shanghai'))

    # 将文件写入 MongoDB GridFS
    file_bytes = await file.read()
    metadata = {
        "project_id": project_id,
        "original_filename": file.filename,
        "content_type": file.content_type,
        "uploaded_at": now.isoformat(),
    }
    gridfs_id = await fs.upload_from_stream(file.filename, file_bytes, metadata=metadata)
    file_id_str = str(gridfs_id)

    # 第一张设为封面：若该项目还没有图片，则 is_cover=1，否则 0
    has_image = db.query(ProjectImageORM).filter(ProjectImageORM.project_id == project_id).first() is not None
    row = ProjectImageORM(
        project_id=project_id,
        file_id=file_id_str,
        is_cover=0 if has_image else 1,
        uploaded_at=now
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return {"image_id": row.image_id, "file_id": file_id_str}


@router.delete("/{project_id}", response_model=dict)
async def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    fs = Depends(get_mongo_fs),
):
    # 校验项目存在且归属当前用户
    project = db.query(ProjectORM).filter(
        ProjectORM.project_id == project_id,
        ProjectORM.user_id == current_user.user_id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在或无权限删除")
    
    # 删除关联的图片记录，并清理 GridFS 文件
    images = db.query(ProjectImageORM).filter(ProjectImageORM.project_id == project_id).all()
    for image in images:
        if image.file_id:
            try:
                await fs.delete(ObjectId(image.file_id))
            except Exception as e:
                # GridFS 删除失败不阻断数据库删除
                print(f"Warning: Failed to delete GridFS file {image.file_id}: {e}")
        db.delete(image)
    
    db.delete(project)
    db.commit()
    
    return {"message": "项目删除成功", "project_id": project_id}


