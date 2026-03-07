from fastapi import APIRouter
from app.api.v1 import users
from app.api.v1 import auth
from app.api.v1 import subjects
from app.api.v1 import tutors
from app.api.v1 import bookings
from app.api.v1 import reviews

from app.api.v1 import wallet 


from app.api.v1 import resources


from app.api.v1 import resources


from app.api.v1 import resources


from app.api.v1 import resources

from app.api.v1 import resources

from app.api.v1 import resources

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["Usuarios"])
api_router.include_router(auth.router, tags=["Autenticación"])
api_router.include_router(subjects.router, prefix="/subjects", tags=["Materias"])
api_router.include_router(tutors.router, prefix="/tutors", tags=["Tutores"])
api_router.include_router(bookings.router, prefix="/bookings", tags=["Reservas"])
api_router.include_router(reviews.router, prefix="/reviews", tags=["Reseñas"])

api_router.include_router(wallet.router, prefix="/wallet", tags=["Billetera Virtual"])

api_router.include_router(resources.router, prefix="/resources", tags=["Resources"])

api_router.include_router(resources.router, prefix="/resources", tags=["Resources"])

api_router.include_router(resources.router, prefix="/resources", tags=["Resources"])

api_router.include_router(resources.router, prefix="/resources", tags=["Resources"])

api_router.include_router(resources.router, prefix="/resources", tags=["Resources"])

api_router.include_router(resources.router, prefix="/resources", tags=["Resources"])

