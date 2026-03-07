from datetime import datetime
from pydantic import BaseModel, ConfigDict


# Datos necesarios para crear una reserva
class BookingCreate(BaseModel):
    tutor_id: int
    subject_id: int
    booking_time: datetime


# actualizar el estado de la reserva
class BookingUpdate(BaseModel):
    status: str


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

    model_config = ConfigDict(from_attributes=True)
