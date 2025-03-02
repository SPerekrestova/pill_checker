from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from supabase import Client, create_client

from app.core.config import settings
from app.core.database import get_db
from app.api.v1.dependencies import get_current_user
from app.models.medication import Medication
from app.schemas.medication import (
    MedicationResponse,
    MedicationCreate,
    PaginatedResponse,
    MedicationStatus,
)
from app.services.ocr_service import recognise

router = APIRouter()

# Initialize Supabase client for storage
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


@router.post("/upload", response_model=MedicationResponse)
async def upload_medication(
    image: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Upload and process a medication image."""
    try:
        # Upload image to Supabase storage
        file_path = f"medications/{current_user['id']}/{image.filename}"
        file_content = await image.read()

        # Upload to storage and check response
        await supabase.storage.from_(settings.SUPABASE_STORAGE_BUCKET).upload(
            file_path, file_content
        )

        # Get public URL
        public_url = f"{settings.storage_url}/{file_path}"

        # Process image with OCR
        ocr_text = await recognise(file_content)

        # Create medication record
        medication_data = MedicationCreate(
            profile_id=current_user["id"],
            scan_url=public_url,
            ocr_text=ocr_text,
            status=MedicationStatus.PENDING,
        )

        medication = Medication(**medication_data.dict())
        db.add(medication)
        await db.commit()
        await db.refresh(medication)

        return MedicationResponse.from_orm(medication)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process medication: {str(e)}",
        )


@router.get("/list", response_model=PaginatedResponse)
async def list_medications(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    page: int = 1,
    size: int = 10,
):
    """List all medications for the current user."""
    # Calculate offset
    skip = (page - 1) * size

    # Get total count using SQLAlchemy 2.0 async compatible syntax
    count_stmt = (
        select(func.count())
        .select_from(Medication)
        .where(Medication.profile_id == current_user["id"])
    )
    count_result = await db.execute(count_stmt)
    total = count_result.scalar_one()

    # Get paginated medications using SQLAlchemy 2.0 async compatible syntax
    stmt = (
        select(Medication)
        .where(Medication.profile_id == current_user["id"])
        .offset(skip)
        .limit(size)
    )
    result = await db.execute(stmt)
    medications = result.scalars().all()

    return PaginatedResponse(
        items=[MedicationResponse.from_orm(med) for med in medications],
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size,
    )


@router.get("/recent", response_model=List[MedicationResponse])
async def get_recent_medications(
    db: AsyncSession = Depends(get_db),
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
    result = await db.execute(stmt)
    medications = result.scalars().all()

    return [MedicationResponse.from_orm(med) for med in medications]


@router.get("/{medication_id}", response_model=MedicationResponse)
async def get_medication_by_id(
    medication_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get a specific medication by ID."""
    stmt = select(Medication).where(
        Medication.id == medication_id, Medication.profile_id == current_user["id"]
    )
    result = await db.execute(stmt)
    medication = result.scalar_one_or_none()

    if not medication:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medication not found")

    return MedicationResponse.from_orm(medication)
