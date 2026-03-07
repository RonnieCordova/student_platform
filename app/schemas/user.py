from pydantic import BaseModel, EmailStr, UUID4
from typing import Optional
from enum import Enum

# defino los roles igual que en el modelo
class UserRole(str, Enum):
    STUDENT = "student"
    TUTOR = "tutor"
    ADMIN = "admin"

# propiedades compartidas por todos
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    is_active: Optional[bool] = True
    # agrego el rol por defecto aqui para que el registro (create_user) no falle
    role: UserRole = UserRole.STUDENT 

# lo que pido cuando alguien se registra 
class UserCreate(UserBase):
    password: str

# lo que le devuelvo a React (Cambiado de UserOut a UserResponse para que coincida con la ruta)
class UserResponse(UserBase):
    public_id: UUID4
    wallet_balance: float
    
    class Config:
        from_attributes = True