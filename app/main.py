from fastapi import FastAPI
from app.db.session import engine, Base
from app.models import user 
from app.models import subject
# Importamos el router nuevo
from app.api.v1.router import api_router
from app.models import tutor_subject
from app.models import booking
from app.models import review
from fastapi.middleware.cors import CORSMiddleware

# Crear tablas (Dev only)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Plataforma de Tutorías", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite peticiones desde cualquier origen (incluyendo tu localhost)
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos los encabezados
)

# Aquí incluimos las rutas de usuarios con un prefijo
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"mensaje": "API funcionando"}