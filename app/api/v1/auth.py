from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.core import security
from app.core.config import settings
from app.models import user as user_model

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/login/access-token")
def login_for_access_token(
    response: Response, # Necesario para setear la cookie
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # Buscamos al usuario
    user = db.query(user_model.User).filter(user_model.User.email == form_data.username).first()
    
    # Verificamos contraseña
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Calculamos expiración
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Creamos el token
    access_token = security.create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    
    # Pasamos de minutos a segundos para la cookie
    expires_in_seconds = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    
    # Seteamos la cookie HttpOnly
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,       # Evita robo por XSS
        max_age=expires_in_seconds,
        expires=expires_in_seconds,
        secure=False,        # Cambiar a True en prod con HTTPS
        samesite="lax",      # Evita ataques CSRF
    )
    
    return {"access_token": access_token, "token_type": "bearer"}