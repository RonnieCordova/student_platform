from fastapi import FastAPI
from app.db.session import engine, Base
# Importamos user para que SQLAlchemy sepa que existe esa tabla antes de crearla
from app.models import user 

# Crear tablas automáticamente
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Plataforma de Tutorías", version="1.0.0")

@app.get("/")
def read_root():
    return {"mensaje": "API conectada y funcionando"}