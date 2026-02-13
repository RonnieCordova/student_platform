from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Datos necesarios para crear una reserva
class BookingCreate(BaseModel):
    tutor_id: int
    subject_id: int
    booking_time: datetime

# Respuesta de la API enriquecida
class BookingResponse(BaseModel):
    id: int
    student_id: int
    tutor_id: int
    subject_id: int
    booking_time: datetime
    status: str
    
    # Campos nuevos para visualización humana
    student_name: str
    tutor_name: str
    subject_name: str

    class Config:
        from_attributes = True