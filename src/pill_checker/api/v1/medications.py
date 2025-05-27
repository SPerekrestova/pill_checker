from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from supabase import Client, create_client

from pill_checker.core.config import settings
from pill_checker.core.database import get_db
from pill_checker.core.logging_config import logger
from pill_checker.models.medication import Medication
from pill_checker.schemas.medication import (
    MedicationCreate,
    MedicationResponse,
    PaginatedResponse,
)
from pill_checker.services.ocr import get_ocr_client
from pill_checker.services.session_service import get_current_user

router = APIRouter()

# Lazy initialization of Supabase client
_supabase_client = None


def get_supabase_client() -> Client:
    """Get or create Supabase client instance."""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    return _supabase_client


@router.post("/upload", response_model=MedicationResponse)
async def upload_medication(
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    ocr_client=Depends(get_ocr_client),
):
    """Upload and process a medication image."""
    try:
        # Get Supabase client
        supabase = get_supabase_client()

        # Upload image to Supabase storage
        file_path = f"medications/{current_user['id']}/{image.filename}"

        file_content = await image.read()
        logger.info(f"File path: {file_path}")

        # Upload to storage and check response
        supabase.storage.from_(settings.SUPABASE_BUCKET_NAME).upload(
            file_path, file_content, file_options={"content-type": image.content_type}
        )

        # Get public URL
        public_url = f"{settings.storage_url}/{file_path}"

        # Process image with OCR
        ocr_text = ocr_client.read_text(file_content)

        # Create medication record
        medication_data = MedicationCreate(
            profile_id=current_user["id"],
            scan_url=public_url,
            scanned_text=ocr_text,
        )

        medication = Medication(**medication_data.model_dump())
        db.add(medication)
        db.commit()
        db.refresh(medication)

        return MedicationResponse.model_validate(medication)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process medication: {str(e)}",
        )


@router.get("/list", response_model=PaginatedResponse)
def list_medications(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    page: int = 1,
    size: int = 10,
):
    """List all medications for the current user."""
    # Calculate offset
    skip = (page - 1) * size

    count_stmt = (
        select(func.count())
        .select_from(Medication)
        .where(Medication.profile_id == current_user["id"])
    )
    count_result = db.execute(count_stmt)
    total = count_result.scalar_one()

    stmt = (
        select(Medication)
        .where(Medication.profile_id == current_user["id"])
        .offset(skip)
        .limit(size)
    )
    result = db.execute(stmt)
    medications = result.scalars().all()

    return PaginatedResponse(
        items=[MedicationResponse.model_validate(med) for med in medications],
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size,
    )


@router.get("/recent", response_model=List[MedicationResponse])
def get_recent_medications(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    limit: int = 5,
):
    """Get recent medications for the current user."""
    stmt = (
        select(Medication)
        .where(Medication.profile_id == current_user["id"])
        .order_by(Medication.scan_date.desc())
        .limit(limit)
    )
    result = db.execute(stmt)
    medications = result.scalars().all()

    return [MedicationResponse.model_validate(med) for med in medications]


@router.get("/{medication_id}", response_model=MedicationResponse)
def get_medication_by_id(
    medication_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get a specific medication by ID."""
    stmt = select(Medication).where(
        Medication.id == medication_id, Medication.profile_id == current_user["id"]
    )
    result = db.execute(stmt)
    medication = result.scalar_one_or_none()

    if not medication:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medication not found")

    return MedicationResponse.model_validate(medication)
