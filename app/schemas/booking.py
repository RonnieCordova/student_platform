from pydantic import BaseModel
from datetime import datetime

# Datos necesarios para crear una reserva
class BookingCreate(BaseModel):
    tutor_id: int
    subject_id: int
    booking_time: datetime

# Respuesta de la API
class BookingResponse(BaseModel):
    id: int
    student_id: int
    tutor_id: int
    subject_id: int
    booking_time: datetime
    status: str

    class Config:
        from_attributes = True