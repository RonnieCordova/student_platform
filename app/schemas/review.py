from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Lo que envia el alumno
class ReviewCreate(BaseModel):
    tutor_id: int
    rating: int  # Deberia ser entre 1 y 5
    comment: Optional[str] = None

# Lo que responde la API
class ReviewResponse(BaseModel):
    id: int
    student_id: int
    tutor_id: int
    rating: int
    comment: Optional[str]
    created_at: datetime
    
    # Nombres para mostrar en el frontend
    student_name: str
    tutor_name: str

    class Config:
        from_attributes = True