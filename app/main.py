from fastapi import FastAPI
from app.db.session import engine, Base
from app.models import user 
from app.models import subject
# Importamos el router nuevo
from app.api.v1.router import api_router
from app.models import tutor_subject
from app.models import booking

# Crear tablas (Dev only)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Plataforma de Tutorías", version="1.0.0")

# Aquí incluimos las rutas de usuarios con un prefijo
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"mensaje": "API funcionando"}