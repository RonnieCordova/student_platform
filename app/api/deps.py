from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer # Necesario para el botón
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import SessionLocal
from app.models import user as user_model

<<<<<<< ours
<<<<<<< ours
<<<<<<< ours

# Esta línea es el "imán" que hace aparecer el botón Authorize en Swagger
# Apunta a la ruta de tu login para que el botón sepa a dónde enviar los datos
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl="/api/v1/login/access-token" 
)

=======
>>>>>>> theirs
=======
>>>>>>> theirs
=======
>>>>>>> theirs
# Esta es la configuración que le dice a FastAPI:
# "Busca el token en el header Authorization: Bearer <token>"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login/access-token")


<<<<<<< ours
<<<<<<< ours
<<<<<<< ours



=======
>>>>>>> theirs
=======
>>>>>>> theirs
=======
>>>>>>> theirs
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


<<<<<<< ours
<<<<<<< ours
<<<<<<< ours
def get_token_from_cookie(request: Request):
    # Intentamos sacar el token de la cookie (para tu Frontend en React)
    token = request.cookies.get("access_token")
    
    # Si no hay cookie (como sucede en Swagger), intentamos sacarlo del Header Authorization
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")
            
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado. Inicia sesión para continuar."
        )
    return token

async def get_current_user(
    # Al poner este Depends(reusable_oauth2), Swagger activa el botón "Authorize"
    token: str = Depends(get_token_from_cookie), 
    db: Session = Depends(get_db),
    _swagger_token: str = Depends(reusable_oauth2) # Solo para activar el candado en la UI
):


=======
>>>>>>> theirs
=======
>>>>>>> theirs
=======
>>>>>>> theirs
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales"
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

<<<<<<< ours
<<<<<<< ours
<<<<<<< ours
    user = db.query(user_model.User).filter(user_model.User.email == email).first()
    if user is None:
        raise credentials_exception
        
    return user


    # 2. Buscamos al dueño del email en la Base de Datos
    user = db.query(user_model.User).filter(user_model.User.email == email).first()
    if user is None:
        raise credentials_exception


    # 2. Buscamos al dueño del email en la Base de Datos
    user = db.query(user_model.User).filter(user_model.User.email == email).first()
    if user is None:
        raise credentials_exception


    # 2. Buscamos al dueño del email en la Base de Datos
    user = db.query(user_model.User).filter(user_model.User.email == email).first()
    if user is None:
        raise credentials_exception

=======
    # 2. Buscamos al dueño del email en la Base de Datos
    user = db.query(user_model.User).filter(user_model.User.email == email).first()
    if user is None:
        raise credentials_exception
>>>>>>> theirs
=======
    # 2. Buscamos al dueño del email en la Base de Datos
    user = db.query(user_model.User).filter(user_model.User.email == email).first()
    if user is None:
        raise credentials_exception
>>>>>>> theirs
=======
    # 2. Buscamos al dueño del email en la Base de Datos
    user = db.query(user_model.User).filter(user_model.User.email == email).first()
    if user is None:
        raise credentials_exception
>>>>>>> theirs

    # 3. Si todo está bien, devolvemos el usuario completo
    return user


async def get_current_admin(current_user: user_model.User = Depends(get_current_user)):
    # verifico si el usuario tiene rol administrador
    if current_user.role != user_model.UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos de administrador")
    return current_user


async def get_current_tutor(current_user: user_model.User = Depends(get_current_user)):
    # verifico si el usuario tiene rol tutor
    if current_user.role != user_model.UserRole.TUTOR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos de tutor")
    return current_user
<<<<<<< ours
<<<<<<< ours
<<<<<<< ours

=======
>>>>>>> theirs
=======
>>>>>>> theirs
=======
>>>>>>> theirs
