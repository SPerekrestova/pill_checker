from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from supabase import Client, create_client

from core.app.core.config import settings
from core.app.core.database import get_db
from core.app.models.models import Medication
from core.app.services.ocr_service import recognise

router = APIRouter()

# Initialize Supabase client for storage
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

@router.post("/upload")
async def upload_medication(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and process a medication image."""
    try:
        # Upload image to Supabase storage
        file_path = f"medications/{file.filename}"
        file_content = await file.read()
        
        storage_response = supabase.storage.from_(settings.SUPABASE_STORAGE_BUCKET).upload(
            file_path,
            file_content
        )

        # Get public URL
        public_url = f"{settings.storage_url}/{file_path}"

        # Process image with OCR
        medication_text = await recognise(file_content)

        # Create medication record
        medication = Medication(
            image_url=public_url,
            ocr_text=medication_text,
            status="pending"
        )
        
        db.add(medication)
        db.commit()
        db.refresh(medication)

        return {
            "message": "Medication uploaded and processed successfully",
            "medication_id": medication.id,
            "status": medication.status
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/list", response_model=List[Medication])
async def list_medications(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 10
):
    """List all medications for the current user."""
    medications = db.query(Medication).offset(skip).limit(limit).all()
    return medications

@router.get("/{medication_id}")
async def get_medication(
    medication_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific medication by ID."""
    medication = db.query(Medication).filter(Medication.id == medication_id).first()
    if not medication:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medication not found"
        )
    return medication 