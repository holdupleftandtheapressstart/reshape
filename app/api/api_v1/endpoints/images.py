import uuid
from typing import Optional, Annotated

from fastapi import APIRouter, Depends, HTTPException, UploadFile, Form, Response
from sqlalchemy.orm import Session

from app import schemas, crud
from app.api import deps


router = APIRouter()


@router.post("/upload", response_model=schemas.Image)
async def upload_image(
    file: UploadFile,
    name: Annotated[str, Form()],
    description: Annotated[Optional[str], Form()],
    db: Session = Depends(deps.get_db),
) -> schemas.Image:
    try:
        fileImage = schemas.ImageUpload(file=file, name=name, description=description)
        return crud.image.create_image(db, image_url=None, image_upload=fileImage)
    except crud.CRUDBadRequestError as exc:
        raise HTTPException(status_code=400, detail=f"{exc.message}")
    except crud.CRUDInternalError as exc:
        raise HTTPException(status_code=500, detail=f"{exc.message}")


@router.post("/", response_model=schemas.Image)
async def create_image(
    image: schemas.ImageUrl,
    db: Session = Depends(deps.get_db),
) -> schemas.Image:
    try:
        return crud.image.create_image(db, image_url=image, image_upload=None)
    except crud.CRUDBadRequestError as exc:
        raise HTTPException(status_code=400, detail=f"{exc.message}")
    except crud.CRUDInternalError as exc:
        raise HTTPException(status_code=500, detail=f"{exc.message}")


@router.get(
    "/{source_image_id}/diff/{target_image_id}", response_model=schemas.ImageDiff
)
async def get_image_diff(
    source_image_id: uuid.UUID,
    target_image_id: uuid.UUID,
    db: Session = Depends(deps.get_db),
) -> schemas.ImageDiff:
    try:
        source_image = crud.image.get_image(db, image_id=source_image_id)
        target_image = crud.image.get_image(db, image_id=target_image_id)
        if not source_image or not target_image:
            raise HTTPException(status_code=404, detail="Image not found")

        diff = crud.image.image_diff(source_image, target_image)
    except crud.CRUDBadRequestError as exc:
        raise HTTPException(status_code=400, detail=f"{exc.message}")
    except crud.CRUDInternalError as exc:
        raise HTTPException(status_code=500, detail=f"{exc.message}")

    return schemas.ImageDiff(
        source_image_id=source_image.id,
        target_image_id=target_image.id,
        diff=diff,
    )


@router.get("/{image_id}", response_model=schemas.Image)
async def get_image(
    image_id: uuid.UUID,
    db: Session = Depends(deps.get_db),
) -> schemas.Image:
    try:
        image = crud.image.get_image(db, image_id=image_id)
    except crud.CRUDBadRequestError as exc:
        raise HTTPException(status_code=400, detail=f"{exc.message}")
    except crud.CRUDInternalError as exc:
        raise HTTPException(status_code=500, detail=f"{exc.message}")

    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    return image


@router.put("/{image_id}", response_class=Response)
async def crop_image(
    image_id: uuid.UUID,
    width: int = 0,
    height: int = 0,
    db: Session = Depends(deps.get_db),
) -> Response:
    try:
        image = crud.image.get_image(db, image_id=image_id)
        if not image:
            raise HTTPException(status_code=404, detail="Images not found")
        _ = crud.image.crop_image(db, image, width, height)
    except crud.CRUDBadRequestError as exc:
        raise HTTPException(status_code=400, detail=f"{exc.message}")
    except crud.CRUDInternalError as exc:
        raise HTTPException(status_code=500, detail=f"{exc.message}")

    return Response(status_code=204)
