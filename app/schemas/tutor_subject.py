from pydantic import BaseModel

# Lo que envía el usuario para postularse
class TutorSubjectCreate(BaseModel):
    subject_id: int
    hourly_rate: float

# Lo que responde la API
class TutorSubjectResponse(BaseModel):
    id: int
    tutor_id: int
    subject_id: int
    hourly_rate: float

    class Config:
        from_attributes = True