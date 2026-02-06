from fastapi import APIRouter
from app.api.v1 import users
from app.api.v1 import auth  #Importar auth

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["Usuarios"])
api_router.include_router(auth.router, tags=["Autenticación"]) #Conectar auth