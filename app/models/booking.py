from sqlalchemy import Column, Integer, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship
from app.db.session import Base
import datetime

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    
    # Relaciones: Quien reserva (alumno), a quien (tutor) y que materia
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tutor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    
    # Fecha y hora de la reserva
    booking_time = Column(DateTime, nullable=False)
    
    # Estado: pending, confirmed, cancelled
    status = Column(String, default="pending")

    # Relaciones para acceder a los objetos completos
    student = relationship("User", foreign_keys=[student_id])
    tutor = relationship("User", foreign_keys=[tutor_id])
    subject = relationship("Subject")