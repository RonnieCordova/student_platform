from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import SessionLocal
from app.models import user as user_model
from app.schemas import user as user_schema
from app.core.security import get_password_hash 
from app.api.deps import get_current_user

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 1. Crear Usuario
@router.post("/", response_model=user_schema.UserResponse)
def create_user(user: user_schema.UserCreate, db: Session = Depends(get_db)):
    # Verificamos si el email ya existe
    db_user = db.query(user_model.User).filter(user_model.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    
    # Creamos el usuario (public_id y wallet_balance se generan solos en la BD)
    new_user = user_model.User(
        email=user.email,
        full_name=user.full_name,
        hashed_password=get_password_hash(user.password), 
        role=user.role
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# 2. Listar Usuarios (Nota de Arquitectura: Proteger con rol ADMIN en el futuro)
@router.get("/", response_model=List[user_schema.UserResponse])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(user_model.User).offset(skip).limit(limit).all()
    return users

# 3. Perfil del usuario actual (Prueba de vida para React y Fuente de la Verdad)
@router.get("/me", response_model=user_schema.UserResponse)
def read_users_me(current_user: user_model.User = Depends(get_current_user)):
    # FastAPI usará UserResponse para filtrar la contraseña y el ID interno automáticamente
    return current_user