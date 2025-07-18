from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, status
from typing import List
import os
import uuid
from minio import Minio
from minio.error import S3Error
import io
from config import settings

router = APIRouter(prefix="/upload", tags=["Upload"])

# Initialize MinIO client
minio_client = Minio(
    settings.minio_endpoint,
    access_key=settings.minio_access_key,
    secret_key=settings.minio_secret_key,
    secure=settings.minio_secure
)

@router.post("/images")
async def upload_images(files: List[UploadFile] = File(...)):
    """Upload multiple images to MinIO"""
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    uploaded_files = []
    
    for file in files:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail=f"File {file.filename} is not an image")
        
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1] if file.filename else '.jpg'
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        try:
            # Read file content
            file_content = await file.read()
            file_size = len(file_content)
            
            # Upload to MinIO
            minio_client.put_object(
                settings.minio_bucket_name,
                unique_filename,
                io.BytesIO(file_content),
                file_size,
                content_type=file.content_type
            )
            
            # Generate public URL
            file_url = f"http://{settings.minio_endpoint}/{settings.minio_bucket_name}/{unique_filename}"
            
            uploaded_files.append({
                "filename": unique_filename,
                "original_filename": file.filename,
                "url": file_url,
                "size": file_size,
                "content_type": file.content_type
            })
            
        except S3Error as e:
            raise HTTPException(status_code=500, detail=f"Failed to upload {file.filename}: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Upload error: {str(e)}")
    
    return {
        "message": f"Successfully uploaded {len(uploaded_files)} files",
        "files": uploaded_files
    }
