from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_  # Necesario para el filtro OR
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
    # Validar que el usuario no se reserve a si mismo
    if booking.tutor_id == current_user.id:
        raise HTTPException(status_code=400, detail="No puedes reservar una clase contigo mismo")

    # Validar que el tutor realmente ensena esa materia
    tutor_relation = db.query(tutor_subject_model.TutorSubject).filter(
        tutor_subject_model.TutorSubject.tutor_id == booking.tutor_id,
        tutor_subject_model.TutorSubject.subject_id == booking.subject_id
    ).first()

    if not tutor_relation:
        raise HTTPException(status_code=400, detail="Este tutor no dicta la materia seleccionada")

    # Crear la reserva
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
    return new_booking

# GET: Listar mis reservas (Como alumno o como tutor)
@router.get("/", response_model=List[booking_schema.BookingResponse])
def read_bookings(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user)
):
    """
    Devuelve las reservas donde el usuario actual es estudiante O tutor.
    """
    bookings = db.query(booking_model.Booking).filter(
        or_(
            booking_model.Booking.student_id == current_user.id,
            booking_model.Booking.tutor_id == current_user.id
        )
    ).offset(skip).limit(limit).all()
    
    return bookings