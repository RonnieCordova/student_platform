from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

# lo que le pedimos al frontend al subir un archivo
class ResourceCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None
    file_url: str # por ahora un string simulando un enlace de AWS S3
    is_premium: bool = False
    price: float = Field(default=0.0, ge=0.0) # ge=0.0 significa "mayor o igual a 0"
    subject_id: int

# lo que le devolvemos a react
class ResourceResponse(BaseModel):
    public_id: UUID # siempre protegemos el id real usando el public_id
    title: str
    description: Optional[str]
    file_url: str
    is_premium: bool
    price: float
    downloads: int
    created_at: datetime
    
    # anidamos informacion para que el frontend no tenga que hacer mas peticiones
    owner_id: int
    subject_id: int

    model_config = {"from_attributes": True} # pydantic v2