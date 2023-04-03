import imagehash
import requests
import uuid

from typing import Set, Tuple, Optional

from PIL import Image as PILImage


from sqlalchemy.orm import Session

import app.models as models
import app.schemas as schemas

from fastapi import UploadFile
from app.core.config import settings

from .exceptions import CRUDBadRequestError, CRUDInternalError


ImagePath = str


class CRUDImage:
    SUPPORTED_IMAGE_FORMAT: Set[str] = {"image/jpeg", "image/png"}

    def store_image(
        self,
        image_url: Optional[schemas.ImageUrl],
        image_upload: Optional[schemas.ImageUpload],
    ) -> models.Image:
        if image_url:
            image_id, image_path = self._store_url_image(image_url.url)
            return models.Image(
                id=str(image_id),
                name=image_url.name,
                description=image_url.description,
                path=image_path,
                hash=self.hash_image(image_path),
            )
        elif image_upload:
            image_id, image_path = self._store_binary_image(image_upload.file)
            return models.Image(
                id=str(image_id),
                name=image_upload.name,
                description=image_upload.description,
                path=image_path,
                hash=self.hash_image(image_path),
            )
        else:
            raise ValueError("Image type not supported")

    def hash_image(self, path: ImagePath) -> str:
        return str(imagehash.phash(PILImage.open(path)))

    def _create_image_metadata(self) -> Tuple[uuid.UUID, ImagePath]:
        image_id = uuid.uuid4()
        image_path = f"{settings.IMAGE_UPLOAD_DIR}/{str(image_id)}"

        return image_id, image_path

    def _store_url_image(self, image_url: str) -> Tuple[uuid.UUID, ImagePath]:
        image_id, image_path = self._create_image_metadata()
        try:
            response = requests.head(image_url)
            if (
                response.headers["content-type"].lower()
                not in self.SUPPORTED_IMAGE_FORMAT
            ):
                raise CRUDBadRequestError("Image format not supported")

            img_data = requests.get(image_url, timeout=0.1).content
            with open(image_path, "wb") as handler:
                handler.write(img_data)
        except requests.exceptions.RequestException:
            raise CRUDBadRequestError("Error while downloading image")
        except CRUDBadRequestError:
            raise
        except Exception:
            raise CRUDInternalError("Error while saving image")

        return image_id, image_path

    def _store_binary_image(self, image: UploadFile) -> Tuple[uuid.UUID, ImagePath]:
        image_id, image_path = self._create_image_metadata()

        content_type = image.content_type
        if (
            content_type
            and content_type.strip().lower() not in self.SUPPORTED_IMAGE_FORMAT
        ):
            raise CRUDBadRequestError("Image format not supported")

        try:
            with open(image_path, "wb") as handler:
                handler.write(image.file.read())
        except Exception:
            raise CRUDInternalError("Error while saving image")

        return image_id, image_path

    def create_image(
        self,
        db: Session,
        image_url: Optional[schemas.ImageUrl],
        image_upload: Optional[schemas.ImageUpload],
    ) -> models.Image:
        db_image = self.store_image(image_url, image_upload)

        db.add(db_image)
        db.commit()
        db.refresh(db_image)
        return db_image

    def get_image(self, db: Session, image_id: uuid.UUID) -> models.Image | None:
        return db.query(models.Image).filter(models.Image.id == str(image_id)).first()

    def image_diff(
        self, source_image: models.Image, target_image: models.Image
    ) -> float:
        source_image_hash = imagehash.hex_to_hash(str(source_image.hash))
        target_image_hash = imagehash.hex_to_hash(str(target_image.hash))

        return source_image_hash - target_image_hash

    def crop_image(
        self, db: Session, image: models.Image, width: int, height: int
    ) -> models.Image:
        try:
            img = PILImage.open(image.path, formats=["JPEG", "PNG"])
            img_width, img_height = img.size
            left = (img_width - width) / 2
            top = (img_height - height) / 2
            right = (img_width + width) / 2
            bottom = (img_height + height) / 2
            new_img = img.crop((left, top, right, bottom))
            new_img.save(image.path, format=img.format)

            image.hash = self.hash_image(str(image.path))  # type: ignore
            db.add(image)
            db.commit()
            db.refresh(image)
        except Exception as e:
            raise CRUDInternalError(f"Error while cropping image {str(e)}")
        return image


image = CRUDImage()
