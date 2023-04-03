import uuid
from enum import Enum

from fastapi import UploadFile

from pydantic import BaseModel, Field, HttpUrl


class ImageType(str, Enum):
    url = "url"
    upload = "upload"


# Shared properties
class ImageBase(BaseModel):
    name: str = Field(..., title="The name of the item", max_length=100)
    description: str | None = Field(
        default=None, title="The description of the item", max_length=300
    )


# Properties to receive on image creation
class ImageUrl(ImageBase):
    url: HttpUrl = Field(title="The URL of the image")


# Properties to receive on image upload
class ImageUpload(ImageBase):
    file: UploadFile = Field(title="The image file")


# Properties shared by models stored in DB
class ImageInDBBase(ImageBase):
    id: uuid.UUID
    hash: str
    path: str

    class Config:
        orm_mode = True


# Properties to return to client
class Image(ImageInDBBase):
    pass


# Properties properties stored in DB
class ImageInDB(ImageInDBBase):
    pass


# Image Diff
class ImageDiff(BaseModel):
    source_image_id: uuid.UUID
    target_image_id: uuid.UUID
    diff: float


# Image Crop
class ImageCrop(BaseModel):
    width: int
    height: int
