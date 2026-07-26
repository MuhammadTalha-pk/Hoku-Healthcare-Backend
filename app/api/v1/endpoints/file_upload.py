"""Profile-picture upload endpoint. Original contributor: Faisal Majeed."""

from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter()
UPLOAD_DIRECTORY = Path("uploads/profile_pictures")
UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)
ALLOWED_CONTENT_TYPES = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024


@router.post("/profile-picture", status_code=status.HTTP_201_CREATED)
async def upload_profile_picture(
    file: UploadFile = File(...),
    _: User = Depends(get_current_user),
) -> dict[str, object]:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Only JPG, PNG, and WEBP images are allowed")
    content = await file.read(MAX_FILE_SIZE + 1)
    try:
        if not content:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="Image size must not exceed 5 MB")
        filename = f"{uuid4().hex}{ALLOWED_CONTENT_TYPES[file.content_type]}"
        path = UPLOAD_DIRECTORY / filename
        path.write_bytes(content)
        return {
            "message": "Profile picture uploaded successfully",
            "original_filename": file.filename,
            "saved_filename": filename,
            "content_type": file.content_type,
            "size_bytes": len(content),
            "profile_picture_url": f"/uploads/profile_pictures/{filename}",
        }
    except OSError as exc:
        raise HTTPException(status_code=500, detail="Unable to save uploaded image") from exc
    finally:
        await file.close()
