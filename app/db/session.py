from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

#Crear el motor
# Echo=True nos permitirá ver las consultas SQL en la consola
engine = create_engine(settings.DATABASE_URL, echo=True)

#Fábrica de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#Base para los modelos
Base = declarative_base()