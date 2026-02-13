from sqlalchemy import Column, Integer, ForeignKey, String, Text, DateTime
from sqlalchemy.orm import relationship
from app.db.session import Base
import datetime

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    
    # Quien opina (student) y de quien opina (tutor)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tutor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # La calificacion (1 al 5) y el texto
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relaciones para saber los nombres despues
    student = relationship("User", foreign_keys=[student_id])
    tutor = relationship("User", foreign_keys=[tutor_id])