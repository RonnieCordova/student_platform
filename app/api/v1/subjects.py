from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models import subject as subject_model
from app.schemas import subject as subject_schema
from app.api.deps import get_current_user # Traemos al guardia de seguridad
from app.models import user as user_model

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 1. Crear Materia PROTEGIDO con Token
@router.post("/", response_model=subject_schema.SubjectResponse, status_code=status.HTTP_201_CREATED)
def create_subject(
    subject: subject_schema.SubjectCreate, 
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user) # <--- El guardia verifica el token aquí
):
    # Verificar si ya existe una materia con ese nombre
    db_subject = db.query(subject_model.Subject).filter(subject_model.Subject.name == subject.name).first()
    if db_subject:
        raise HTTPException(status_code=400, detail="Ya existe una materia con ese nombre")
    
    # Crear la nueva materia
    new_subject = subject_model.Subject(
        name=subject.name,
        description=subject.description
    )
    db.add(new_subject)
    db.commit()
    db.refresh(new_subject)
    return new_subject

# 2. Listar Materias (Cualquiera puede verlas)
@router.get("/", response_model=list[subject_schema.SubjectResponse])
def read_subjects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    subjects = db.query(subject_model.Subject).offset(skip).limit(limit).all()
    return subjects