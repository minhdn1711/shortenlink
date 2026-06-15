from pathlib import Path

from fastapi import APIRouter, File, UploadFile
from pydantic import BaseModel

from app.config import settings
from app.utils.assets import public_upload_url
from app.utils.uploads import save_meta_image

router = APIRouter(prefix="/uploads", tags=["uploads"])


class MetaImageUploadResponse(BaseModel):
    url: str
    filename: str


@router.post("/meta-image", response_model=MetaImageUploadResponse)
async def upload_meta_image(
    file: UploadFile = File(...),
) -> MetaImageUploadResponse:
    upload_dir = Path(settings.upload_dir)
    filename = await save_meta_image(file, upload_dir, settings.max_upload_bytes)
    return MetaImageUploadResponse(
        url=public_upload_url(filename),
        filename=filename,
    )
