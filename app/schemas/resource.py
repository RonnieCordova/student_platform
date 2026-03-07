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
