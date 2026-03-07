
from sqlalchemy import Column, String, Text, Boolean, Integer, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

# SOLUCIÓN 1: Importamos directamente desde session para romper el bucle infinito
from app.db.session import Base

class Resource(Base):
    __tablename__ = "resources"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    file_url = Column(String, nullable=False)
    file_type = Column(String) 
    subject = Column(String, index=True)
    
    downloads = Column(Integer, default=0)
    is_premium = Column(Boolean, default=False)
    
    # SOLUCIÓN 2: Cambiamos UUID por Integer para que coincida con el ID de la tabla users
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relación con el usuario que sube el archivo
    owner = relationship("User", back_populates="resources")

from sqlalchemy import Column, Integer, ForeignKey, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.db.session import Base
import datetime


class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String, nullable=False, index=True)
    subject = Column(String, nullable=False, index=True)
    file_type = Column(String, nullable=False)
    file_url = Column(String, nullable=False)
    is_premium = Column(Boolean, default=False, nullable=False)
    is_approved = Column(Boolean, default=False, nullable=False)
    downloads = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    owner = relationship("User")
