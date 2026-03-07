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
from app.models.subject import Subject
from app.api.deps import get_current_user

router = APIRouter()

SESSION_PRICE = 15.00 
PLATFORM_FEE_PERCENTAGE = 0.15 

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
    if booking.tutor_id == current_user.id:
        raise HTTPException(status_code=400, detail="No puedes reservar una clase contigo mismo")

    tutor_relation = db.query(tutor_subject_model.TutorSubject).filter(
        tutor_subject_model.TutorSubject.tutor_id == booking.tutor_id,
        tutor_subject_model.TutorSubject.subject_id == booking.subject_id
    ).first()

    if not tutor_relation:
        raise HTTPException(status_code=400, detail="Este tutor no dicta la materia seleccionada")

    if current_user.wallet_balance < SESSION_PRICE:
        raise HTTPException(
            status_code=400, 
            detail=f"Saldo insuficiente. La tutoría cuesta ${SESSION_PRICE} y tienes ${current_user.wallet_balance}"
        )

    # --- RETENCIÓN ESCROW: Update directo a la base de datos ---
    # fuerzo a sql a hacer la resta matematicamente
    db.query(user_model.User).filter(user_model.User.id == current_user.id).update(
        {"wallet_balance": user_model.User.wallet_balance - SESSION_PRICE}
    )
    
    # calculo el nuevo saldo para dejarlo escrito en el recibo
    nuevo_saldo = current_user.wallet_balance - SESSION_PRICE
    
    # creo el recibo financiero
    retention_tx = wallet_transaction_model.WalletTransaction(
        user_id=current_user.id,
        amount=-SESSION_PRICE, 
        description=f"Retención de fondos por reserva de tutoría (Tutor ID: {booking.tutor_id})",
        balance_after_transaction=nuevo_saldo
    )
    
    # creo la reserva
    new_booking = booking_model.Booking(
        student_id=current_user.id,
        tutor_id=booking.tutor_id,
        subject_id=booking.subject_id,
        booking_time=booking.booking_time,
        status="pending"
    )
    
    db.add(retention_tx)
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)

    subject_info = db.query(Subject).filter(Subject.id == booking.subject_id).first()
    subject_name = subject_info.name if subject_info else "Materia Desconocida"

    tutor_info = db.query(user_model.User).filter(user_model.User.id == booking.tutor_id).first()
    tutor_name = tutor_info.full_name if (tutor_info and tutor_info.full_name) else (tutor_info.email if tutor_info else "Tutor")

    return {
        "id": new_booking.id,
        "student_id": new_booking.student_id,
        "tutor_id": new_booking.tutor_id,
        "subject_id": new_booking.subject_id,
        "booking_time": new_booking.booking_time,
        "status": new_booking.status,
        "student_name": current_user.full_name or current_user.email,
        "tutor_name": tutor_name,
        "subject_name": subject_name
    }

# GET: Listar reservas
@router.get("/", response_model=List[booking_schema.BookingResponse])
def read_bookings(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user)
):
    bookings = db.query(booking_model.Booking).filter(
        or_(
            booking_model.Booking.student_id == current_user.id,
            booking_model.Booking.tutor_id == current_user.id
        )
    ).offset(skip).limit(limit).all()
    
    results = []
    for booking in bookings:
        student_name = "Estudiante"
        if booking.student:
            student_name = booking.student.full_name or booking.student.email
            
        tutor_name = "Tutor"
        if booking.tutor:
            tutor_name = booking.tutor.full_name or booking.tutor.email
            
        subject_name = booking.subject.name if booking.subject else "Desconocida"

        results.append({
            "id": booking.id,
            "student_id": booking.student_id,
            "tutor_id": booking.tutor_id,
            "subject_id": booking.subject_id,
            "booking_time": booking.booking_time,
            "status": booking.status,
            "student_name": student_name,
            "tutor_name": tutor_name,
            "subject_name": subject_name
        })
    return results

# PATCH: Actualizar estado de la reserva
@router.patch("/{booking_id}", response_model=booking_schema.BookingResponse)
def update_booking_status(
    booking_id: int,
    booking_update: booking_schema.BookingUpdate,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user)
):
    booking = db.query(booking_model.Booking).filter(booking_model.Booking.id == booking_id).first()

    if not booking:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")

    if booking.tutor_id != current_user.id:
        raise HTTPException(
            status_code=403, 
            detail="Solo el tutor de esta clase puede aprobar o rechazar la reserva"
        )

    if booking_update.status == "rejected" and booking.status == "pending":
        # devuelvo el dinero directo a la bd
        db.query(user_model.User).filter(user_model.User.id == booking.student_id).update(
            {"wallet_balance": user_model.User.wallet_balance + SESSION_PRICE}
        )
        
        student = db.query(user_model.User).filter(user_model.User.id == booking.student_id).first()
        if student:
            refund_tx = wallet_transaction_model.WalletTransaction(
                user_id=student.id,
                amount=SESSION_PRICE,
                description=f"Reembolso: El tutor rechazó tu reserva #{booking.id}",
                balance_after_transaction=student.wallet_balance
            )
            db.add(refund_tx)

    elif booking_update.status == "completed" and booking.status == "confirmed":
        tutor_payment = SESSION_PRICE * (1 - PLATFORM_FEE_PERCENTAGE)
        
        # liquido el pago directo a la bd
        db.query(user_model.User).filter(user_model.User.id == current_user.id).update(
            {"wallet_balance": user_model.User.wallet_balance + tutor_payment}
        )
        
        # recargo al tutor en memoria para leer su nuevo saldo
        db.refresh(current_user)
        
        payment_tx = wallet_transaction_model.WalletTransaction(
            user_id=current_user.id,
            amount=tutor_payment,
            description=f"Pago por tutoría completada #{booking.id} (Comisión {PLATFORM_FEE_PERCENTAGE*100}% aplicada)",
            balance_after_transaction=current_user.wallet_balance
        )
        db.add(payment_tx)

    booking.status = booking_update.status
    db.commit()
    db.refresh(booking)

    student_name = booking.student.full_name or booking.student.email if booking.student else "Estudiante"
    tutor_name = booking.tutor.full_name or booking.tutor.email if booking.tutor else "Tutor"
    subject_name = booking.subject.name if booking.subject else "Desconocida"

    return {
        "id": booking.id,
        "student_id": booking.student_id,
        "tutor_id": booking.tutor_id,
        "subject_id": booking.subject_id,
        "booking_time": booking.booking_time,
        "status": booking.status,
        "student_name": student_name,
        "tutor_name": tutor_name,
        "subject_name": subject_name
    }