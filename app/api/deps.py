# app/api/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import SessionLocal
from app.models import user as user_model

# le digo a fastapi (y a swagger) en que endpoint debe autenticarse para conseguir el token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login/access-token")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# extraigo el usuario actual leyendo su token
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 1. intento decodificar el token con mi llave maestra
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # 2. busco al dueño del email en mi base de datos
    user = db.query(user_model.User).filter(user_model.User.email == email).first()
    if user is None:
        raise credentials_exception
        
    # 3. si todo esta bien, devuelvo el perfil completo del usuario
    return user

# --- CONTROL DE ACCESOS POR ROL (RBAC) ---

# exijo que el usuario tenga credenciales de tutor
async def get_current_tutor(
    current_user: user_model.User = Depends(get_current_user)
):
    # verifico si el rol es el correcto, si no, lo bloqueo con un 403
    if current_user.role not in ["tutor", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes los permisos necesarios. Se requiere rol de Tutor."
        )
    return current_user

# exijo que el usuario sea el administrador del sistema
async def get_current_admin(
    current_user: user_model.User = Depends(get_current_user)
):
    # bloqueo el paso a cualquier rol que no sea 'admin'
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Se requieren privilegios de Administrador."
        )
    return current_user