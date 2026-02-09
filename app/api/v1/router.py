from fastapi import APIRouter
from app.api.v1 import users
from app.api.v1 import auth
from app.api.v1 import subjects
from app.api.v1 import tutors

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["Usuarios"])
api_router.include_router(auth.router, tags=["Autenticación"])
api_router.include_router(subjects.router, prefix="/subjects", tags=["Materias"])
api_router.include_router(tutors.router, prefix="/tutors", tags=["Tutores"])