from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile, status

router = APIRouter(
    prefix="/api/files",
    tags=["File Upload"],
)

UPLOAD_DIRECTORY = Path("uploads/profile_pictures")
UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)

ALLOWED_CONTENT_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


@router.post(
    "/profile-picture",
    status_code=status.HTTP_201_CREATED,
)
async def upload_profile_picture(
    file: UploadFile = File(...),
):
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPG, PNG, and WEBP images are allowed.",
        )

    file_content = await file.read()

    if not file_content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Image size must not exceed 5 MB.",
        )

    extension = ALLOWED_CONTENT_TYPES[file.content_type]
    unique_filename = f"{uuid4().hex}{extension}"
    saved_path = UPLOAD_DIRECTORY / unique_filename

    try:
        saved_path.write_bytes(file_content)
    except OSError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to save the uploaded image.",
        ) from error
    finally:
        await file.close()

    return {
        "message": "Profile picture uploaded successfully.",
        "original_filename": file.filename,
        "saved_filename": unique_filename,
        "content_type": file.content_type,
        "size_bytes": len(file_content),
        "profile_picture_url": f"/uploads/profile_pictures/{unique_filename}",
    }