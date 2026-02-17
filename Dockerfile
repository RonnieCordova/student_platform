# 1. Base Image: Usamos SLIM para reducir superficie de ataque
FROM python:3.9-slim

# 2. Security Best Practice: Evitar correr como Root
RUN useradd -m -u 1000 appuser

# 3. Variables de entorno para optimizacion
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/home/appuser/.local/bin:$PATH"

# 4. Establecemos directorio de trabajo
WORKDIR /app

# 5. Instalar dependencias del sistema y limpiar cache apt
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 6. Copiamos los requisitos y asignamos permisos
COPY --chown=appuser:appuser requirements.txt .

# 7. Cambiamos al usuario sin privilegios ANTES de instalar paquetes
USER appuser

# 8. Instalamos dependencias de Python
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 9. Copiamos el codigo fuente
COPY --chown=appuser:appuser . .

# 10. Documentamos el puerto
EXPOSE 8000

# 11. Ejecutamos la aplicacion
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]