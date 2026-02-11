from sqlalchemy import Column, Integer, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.db.session import Base

class TutorSubject(Base):
    __tablename__ = "tutor_subjects"

    id = Column(Integer, primary_key=True, index=True)
    
    # Claves foráneas (Los puentes)
    tutor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    
    # El precio por hora de este tutor para esta materia
    hourly_rate = Column(Float, nullable=False)

    # Acceder a .tutor.full_name o .subject.name
    tutor = relationship("User") 
    subject = relationship("Subject")