from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

# importo desde session para evitar bucles infinitos en la arquitectura
from app.db.session import Base

class WalletTransaction(Base):
    __tablename__ = "wallet_transactions"
    
    # llave primaria publica y segura para react
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # uso Integer estrictamente para que coincida con el id interno del User
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    amount = Column(Float, nullable=False)
    description = Column(String, nullable=False)
    # guardo una foto del saldo en ese momento para auditorias
    balance_after_transaction = Column(Float, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # relaciono esto con el usuario dueño de la transaccion
    user = relationship("User", back_populates="transactions")