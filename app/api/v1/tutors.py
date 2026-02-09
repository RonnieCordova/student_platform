from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models import tutor_subject as tutor_subject_model
from app.schemas import tutor_subject as tutor_subject_schema
from app.models import user as user_model
from app.api.deps import get_current_user

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/me/subjects", response_model=tutor_subject_schema.TutorSubjectResponse)
def add_subject_to_me(
    item: tutor_subject_schema.TutorSubjectCreate,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user)
):
    """
    El usuario logueado se asigna una materia para enseñar.
    """
    # 1. Verificar que no esté repitiendo la materia
    existing_entry = db.query(tutor_subject_model.TutorSubject).filter(
        tutor_subject_model.TutorSubject.tutor_id == current_user.id,
        tutor_subject_model.TutorSubject.subject_id == item.subject_id
    ).first()

    if existing_entry:
        raise HTTPException(status_code=400, detail="Ya estás inscrito en esta materia")

    # 2. Crear la relación
    new_entry = tutor_subject_model.TutorSubject(
        tutor_id=current_user.id,
        subject_id=item.subject_id,
        hourly_rate=item.hourly_rate
    )
    
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    return new_entry