from fastapi import FastAPI
from app.db.session import engine, Base
from app.models import user 
# Importamos el router nuevo
from app.api.v1 import users 

# Crear tablas (Dev only)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Plataforma de Tutorías", version="1.0.0")

# Aquí incluimos las rutas de usuarios con un prefijo
app.include_router(users.router, prefix="/users", tags=["Usuarios"])

@app.get("/")
def read_root():
    return {"mensaje": "API funcionando"}