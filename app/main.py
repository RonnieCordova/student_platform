from fastapi import FastAPI

app = FastAPI(
    title="Plataforma de Tutorías Estudiantiles",
    description="API para conectar estudiantes y tutores. Proyecto para Portafolio Cloud.",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"mensaje": "Bienvenido a la API de Tutorías - Estado: Activo"}

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "tutor-api"}