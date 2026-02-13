from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.db.session import SessionLocal
from app.models import booking as booking_model
from app.schemas import booking as booking_schema
from app.models import user as user_model
from app.models import tutor_subject as tutor_subject_model
from app.api.deps import get_current_user

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# POST: Crear una nueva reserva
@router.post("/", response_model=booking_schema.BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(
    booking: booking_schema.BookingCreate,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user)
):
    # Validacion de auto-reserva
    if booking.tutor_id == current_user.id:
        raise HTTPException(status_code=400, detail="No puedes reservar una clase contigo mismo")

    # Validacion de competencia del tutor
    tutor_relation = db.query(tutor_subject_model.TutorSubject).filter(
        tutor_subject_model.TutorSubject.tutor_id == booking.tutor_id,
        tutor_subject_model.TutorSubject.subject_id == booking.subject_id
    ).first()

    if not tutor_relation:
        raise HTTPException(status_code=400, detail="Este tutor no dicta la materia seleccionada")

    # Creacion del registro
    new_booking = booking_model.Booking(
        student_id=current_user.id,
        tutor_id=booking.tutor_id,
        subject_id=booking.subject_id,
        booking_time=booking.booking_time,
        status="pending"
    )
    
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)

    # Construccion manual de la respuesta para el POST (para incluir nombres)
    return {
        "id": new_booking.id,
        "student_id": new_booking.student_id,
        "tutor_id": new_booking.tutor_id,
        "subject_id": new_booking.subject_id,
        "booking_time": new_booking.booking_time,
        "status": new_booking.status,
        "student_name": current_user.full_name or current_user.email,
        "tutor_name": tutor_relation.tutor.full_name or tutor_relation.tutor.email,
        "subject_name": tutor_relation.subject.name
    }

# GET: Listar reservas enriquecidas
@router.get("/", response_model=List[booking_schema.BookingResponse])
def read_bookings(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user)
):
    # Filtrar reservas donde el usuario es estudiante o tutor
    bookings = db.query(booking_model.Booking).filter(
        or_(
            booking_model.Booking.student_id == current_user.id,
            booking_model.Booking.tutor_id == current_user.id
        )
    ).offset(skip).limit(limit).all()
    
    # Mapeo de objetos ORM a diccionario con nombres legibles
    results = []
    for booking in bookings:
        results.append({
            "id": booking.id,
            "student_id": booking.student_id,
            "tutor_id": booking.tutor_id,
            "subject_id": booking.subject_id,
            "booking_time": booking.booking_time,
            "status": booking.status,
            # Obtencion de nombres a traves de las relaciones SQLAlchemy
            "student_name": booking.student.full_name if booking.student.full_name else booking.student.email,
            "tutor_name": booking.tutor.full_name if booking.tutor.full_name else booking.tutor.email,
            "subject_name": booking.subject.name
        })
    
    return results