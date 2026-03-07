from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.db.session import SessionLocal
from app.models import booking as booking_model
from app.schemas import booking as booking_schema
from app.models import user as user_model
from app.models import tutor_subject as tutor_subject_model
from app.models import wallet_transaction as wallet_transaction_model
from app.api.deps import get_current_user

router = APIRouter()
PLATFORM_COMMISSION_RATE = 0.15


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
    current_user: user_model.User = Depends(get_current_user),
):
    # Validacion de auto-reserva
    if booking.tutor_id == current_user.id:
        raise HTTPException(status_code=400, detail="No puedes reservar una clase contigo mismo")

    # Validacion de competencia del tutor
    tutor_relation = db.query(tutor_subject_model.TutorSubject).filter(
        tutor_subject_model.TutorSubject.tutor_id == booking.tutor_id,
        tutor_subject_model.TutorSubject.subject_id == booking.subject_id,
    ).first()

    if not tutor_relation:
        raise HTTPException(status_code=400, detail="Este tutor no dicta la materia seleccionada")

    # obtengo el precio por hora del tutor para esta materia
    total_cost = float(tutor_relation.hourly_rate)

    # verifico si tiene saldo disponible
    if float(current_user.wallet_balance) < total_cost:
        raise HTTPException(status_code=400, detail="Fondos insuficientes en la billetera")

    # descuento el saldo de la billetera del estudiante
    current_user.wallet_balance = float(current_user.wallet_balance) - total_cost

    # guardo la transaccion de debito en la bd
    student_wallet_tx = wallet_transaction_model.WalletTransaction(
        user_id=current_user.id,
        amount=-total_cost,
        transaction_type="booking_debit",
        description=f"Reserva creada para tutor #{booking.tutor_id}",
    )
    db.add(student_wallet_tx)

    # guardo la reserva en estado pendiente
    new_booking = booking_model.Booking(
        student_id=current_user.id,
        tutor_id=booking.tutor_id,
        subject_id=booking.subject_id,
        booking_time=booking.booking_time,
        status="pending",
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
        "subject_name": tutor_relation.subject.name,
    }


# GET: Listar reservas enriquecidas
@router.get("/", response_model=List[booking_schema.BookingResponse])
def read_bookings(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    # Filtrar reservas donde el usuario es estudiante o tutor
    bookings = db.query(booking_model.Booking).filter(
        or_(
            booking_model.Booking.student_id == current_user.id,
            booking_model.Booking.tutor_id == current_user.id,
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
            "subject_name": booking.subject.name,
        })

    return results


# Actualizar estado de la reserva (Aceptar/Rechazar)
@router.patch("/{booking_id}", response_model=booking_schema.BookingResponse)
def update_booking_status(
    booking_id: int,
    booking_update: booking_schema.BookingUpdate,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    # Buscar la reserva por ID
    booking = db.query(booking_model.Booking).filter(booking_model.Booking.id == booking_id).first()

    if not booking:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")

    # Verificar seguridad: Solo el tutor asignado puede cambiar el estado
    if booking.tutor_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Solo el tutor de esta clase puede aprobar o rechazar la reserva",
        )

    # Actualizar el estado
    booking.status = booking_update.status
    db.commit()
    db.refresh(booking)

    # Reconstruir la respuesta con los nombres
    return {
        "id": booking.id,
        "student_id": booking.student_id,
        "tutor_id": booking.tutor_id,
        "subject_id": booking.subject_id,
        "booking_time": booking.booking_time,
        "status": booking.status,
        "student_name": booking.student.full_name or booking.student.email,
        "tutor_name": booking.tutor.full_name or booking.tutor.email,
        "subject_name": booking.subject.name,
    }


@router.put("/{booking_id}/complete", response_model=booking_schema.BookingResponse)
def complete_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    # busco la reserva para completarla
    booking = db.query(booking_model.Booking).filter(booking_model.Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")

    # verifico si es tutor de la reserva o admin
    is_admin = current_user.role == user_model.UserRole.ADMIN
    is_tutor_owner = booking.tutor_id == current_user.id and current_user.role == user_model.UserRole.TUTOR
    if not (is_admin or is_tutor_owner):
        raise HTTPException(status_code=403, detail="No tienes permisos para completar esta reserva")

    # verifico que la reserva siga en estado pendiente
    if booking.status.lower() == "completed":
        raise HTTPException(status_code=400, detail="La reserva ya fue completada")

    tutor_relation = db.query(tutor_subject_model.TutorSubject).filter(
        tutor_subject_model.TutorSubject.tutor_id == booking.tutor_id,
        tutor_subject_model.TutorSubject.subject_id == booking.subject_id,
    ).first()
    if not tutor_relation:
        raise HTTPException(status_code=400, detail="No se encontró tarifa para esta reserva")

    # calculo pago del tutor aplicando comisión de plataforma
    gross_amount = float(tutor_relation.hourly_rate)
    tutor_amount = gross_amount * (1 - PLATFORM_COMMISSION_RATE)

    tutor_user = db.query(user_model.User).filter(user_model.User.id == booking.tutor_id).first()
    if not tutor_user:
        raise HTTPException(status_code=404, detail="Tutor no encontrado")

    # sumo el saldo al tutor
    tutor_user.wallet_balance = float(tutor_user.wallet_balance) + tutor_amount

    # guardo la transaccion de crédito del tutor
    tutor_wallet_tx = wallet_transaction_model.WalletTransaction(
        user_id=tutor_user.id,
        amount=tutor_amount,
        transaction_type="booking_credit",
        description=f"Pago por reserva #{booking.id}",
    )
    db.add(tutor_wallet_tx)

    # marco la reserva como completada
    booking.status = "completed"

    db.commit()
    db.refresh(booking)

    return {
        "id": booking.id,
        "student_id": booking.student_id,
        "tutor_id": booking.tutor_id,
        "subject_id": booking.subject_id,
        "booking_time": booking.booking_time,
        "status": booking.status,
        "student_name": booking.student.full_name or booking.student.email,
        "tutor_name": booking.tutor.full_name or booking.tutor.email,
        "subject_name": booking.subject.name,
    }
