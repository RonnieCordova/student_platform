from pydantic import BaseModel, UUID4
from typing import Optional
from datetime import datetime

class ResourceBase(BaseModel):
    title: str
    description: Optional[str] = None
    file_url: str
    file_type: str
    subject: str
    is_premium: bool = False

# los datos que manda React cuando suben un PDF
class ResourceCreate(ResourceBase):
    pass 

# los datos que recibe React para pintar las tarjetas en la boveda
class ResourceOut(ResourceBase):
    id: UUID4
    downloads: int
    created_at: datetime
    
    class Config:
        from_attributes = True


from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ResourceCreate(BaseModel):
    title: str
    subject: str
    file_type: str
    file_url: str
    is_premium: bool = False


class ResourceResponse(BaseModel):
    id: int
    owner_id: int
    title: str
    subject: str
    file_type: str
    file_url: str
    is_premium: bool
    is_approved: bool
    downloads: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResourceDownloadResponse(BaseModel):
    file_url: str
    downloads: int

    model_config = ConfigDict(from_attributes=True)
