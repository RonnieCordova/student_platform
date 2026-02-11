from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models import tutor_subject as tutor_subject_model
from app.schemas import tutor_subject as tutor_subject_schema
from app.models import user as user_model
from app.models import subject as subject_model
from app.api.deps import get_current_user

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# POST: Asignar materia al usuario actual
@router.post("/me/subjects", response_model=tutor_subject_schema.TutorSubjectResponse)
def add_subject_to_me(
    item: tutor_subject_schema.TutorSubjectCreate,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user)
):
    # Validar si la relacion ya existe para evitar duplicados
    existing_entry = db.query(tutor_subject_model.TutorSubject).filter(
        tutor_subject_model.TutorSubject.tutor_id == current_user.id,
        tutor_subject_model.TutorSubject.subject_id == item.subject_id
    ).first()

    if existing_entry:
        raise HTTPException(status_code=400, detail="Materia ya asignada a este tutor")

    # Crear nuevo registro
    new_entry = tutor_subject_model.TutorSubject(
        tutor_id=current_user.id,
        subject_id=item.subject_id,
        hourly_rate=item.hourly_rate
    )
    
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    return new_entry

# GET: Listar tutores (Buscador publico)
@router.get("/", response_model=List[tutor_subject_schema.TutorCard])
def search_tutors(
    subject_id: Optional[int] = None, 
    skip: int = 0, 
    limit: int = 20, 
    db: Session = Depends(get_db)
):
    # Consulta base con eager loading implicito si estan definidas las relaciones
    query = db.query(tutor_subject_model.TutorSubject)
    
    # Aplicar filtro por materia si se proporciona
    if subject_id:
        query = query.filter(tutor_subject_model.TutorSubject.subject_id == subject_id)
    
    results = query.offset(skip).limit(limit).all()
    
    # Mapeo manual para ajustar respuesta al schema TutorCard
    output_list = []
    for item in results:
        # Obtener nombre del tutor o email como fallback
        tutor_name = item.tutor.full_name if item.tutor.full_name else item.tutor.email
        
        output_list.append({
            "tutor_id": item.tutor_id,
            "tutor_name": tutor_name,
            "subject_name": item.subject.name,
            "hourly_rate": item.hourly_rate
        })
        
    return output_list