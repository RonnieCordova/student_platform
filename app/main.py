from fastapi import FastAPI
from app.db.session import engine, Base
from app.models import user
from app.models import subject
from app.models import tutor_subject
from app.models import booking
from app.models import review
from app.models import wallet_transaction
from app.models import resource
from app.api.v1.router import api_router
from fastapi.middleware.cors import CORSMiddleware
import app.db.base

# Crear tablas (Dev only)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Plataforma de Tutorías", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Permite peticiones solo del localhost en el puerto 5173


    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "Origin", "X-Requested-With"],
)

# Aquí incluimos las rutas de usuarios con un prefijo
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def read_root():
    return {"mensaje": "API funcionando"}
