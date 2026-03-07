from sqlalchemy import Column, Float, Integer, String, Boolean, Enum
from sqlalchemy.orm import relationship
from app.db.session import Base
import enum

class UserRole(str, enum.Enum):
    STUDENT = "student"
    TUTOR = "tutor"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.STUDENT)
    is_active = Column(Boolean, default=True)


# motor financiero
    wallet_balance = Column(Float, default=0.0)
    
    # conecto el usuario con su historial de transacciones
    transactions = relationship("WalletTransaction", back_populates="user")