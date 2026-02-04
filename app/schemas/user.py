from pydantic import BaseModel, EmailStr
from typing import Optional
from app.models.user import UserRole

#lectura y escritura
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    role: UserRole = UserRole.STUDENT # Por defecto es estudiante

# Input necesario para crear un usuario
class UserCreate(UserBase):
    password: str

# devolver al frontend (Output)
class UserResponse(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True