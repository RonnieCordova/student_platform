from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

# importo desde session para evitar dependencias circulares
from app.db.session import Base

class Resource(Base):
    __tablename__ = "resources"
    
    # llaves de arquitectura (interna para DB, publica para frontend)
    id = Column(Integer, primary_key=True, index=True)
    public_id = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, index=True)
    
    # metadatos del archivo
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    file_url = Column(String, nullable=False) # simularemos la url de un bucket s3
    
    # monetizacion
    is_premium = Column(Boolean, default=False)
    price = Column(Float, default=0.0)
    
    # metricas
    downloads = Column(Integer, default=0)
    
    # relaciones (uso Integer para optimizar los JOINs)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # navego a los objetos completos
    owner = relationship("User")
    subject = relationship("Subject")