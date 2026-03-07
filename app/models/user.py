from sqlalchemy import Column, Integer, String, Boolean, Enum, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.session import Base
import enum
import uuid


class UserRole(str, enum.Enum):
    STUDENT = "student"
    TUTOR = "tutor"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    # Llave primaria interna (Rápida, mantiene tu código actual a salvo)
    id = Column(Integer, primary_key=True, index=True)

    public_id = Column(String(36), unique=True, index=True, nullable=False, default=lambda: str(uuid.uuid4()))


    # Capa de Seguridad Cloud: Identificador público para evitar ataques IDOR
    public_id = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, index=True)



    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.STUDENT)
    is_active = Column(Boolean, default=True)
    wallet_balance = Column(Float, default=0.0, nullable=False)


    # --- NUEVOS MÓDULOS DE NEGOCIO ---
    
    # Motor Financiero (Billetera)
    wallet_balance = Column(Float, default=0.0)
    
    # Relaciones con las nuevas tablas (Asegúrate de tener creados wallet_transaction.py y resource.py)
    transactions = relationship("WalletTransaction", back_populates="user")
    resources = relationship("Resource", back_populates="owner")
    
    # Nota para ti: Si en el futuro necesitas relacionar tus bookings, se vería así:
    # bookings = relationship("Booking", back_populates="user")



