from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.session import engine, Base
from app.api.v1.router import api_router

# importo el índice de mis modelos para que SQLAlchemy construya todas las tablas de golpe
import app.db.base 

# construyo las tablas (Dev only)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Plataforma de Tutorías", version="1.0.0")

# --- PERÍMETRO DE SEGURIDAD: CORS ---
# defino explícitamente los dominios de mi frontend en los que confío
origins = [
    "http://localhost:3000", # puerto por defecto de react
    "http://127.0.0.1:3000",
    "http://localhost:5173", # puerto por defecto si usas vite
]

# configuro el escudo
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True, # como esto es True, origins NO puede ser ["*"]
    allow_methods=["*"],    # permito todos los metodos (GET, POST, PATCH, etc.)
    allow_headers=["*"],    # permito todos los encabezados
)

# incluyo el enrutador principal que contiene todos mis módulos
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"mensaje": "API de Tutorías funcionando y segura"}