from sqlalchemy import Column, String, Float, ForeignKey, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

# SOLUCIÓN 1: Importamos directamente desde session para romper el bucle infinito
from app.db.session import Base 

class WalletTransaction(Base):
    __tablename__ = "wallet_transactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # SOLUCIÓN 2: Cambiamos UUID por Integer para que coincida perfectamente con el ID de tu tabla users
    user_id = Column(Integer, ForeignKey("users.id")) 
    
    amount = Column(Float, nullable=False)
    description = Column(String, nullable=False)
    balance_after_transaction = Column(Float, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relación con el usuario
    user = relationship("User", back_populates="transactions")

from sqlalchemy import Column, Integer, ForeignKey, Float, String, DateTime
from sqlalchemy.orm import relationship
from app.db.session import Base
import datetime


class WalletTransaction(Base):
    __tablename__ = "wallet_transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    transaction_type = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    user = relationship("User")
