from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from pill_checker.core.database import get_db
from pill_checker.core.logging_config import logger
from pill_checker.models.medication import Medication
from pill_checker.schemas.medication import (
    MedicationCreate,
    MedicationResponse,
    PaginatedResponse,
)
from pill_checker.services.biomed_ner_client import get_ner_client, MedicalNERClient
from pill_checker.services.medication_processing import process_medication_text
from pill_checker.services.ocr import get_ocr_client
from pill_checker.services.session_service import get_current_user
from pill_checker.services.storage import get_storage_service

router = APIRouter()


@router.post("/upload", response_model=MedicationResponse)
async def upload_medication(
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    ocr_client=Depends(get_ocr_client),
    ner_client: MedicalNERClient = Depends(get_ner_client),
):
    """
    Upload and process a medication image.

    This endpoint:
    1. Uploads the image to storage
    2. Extracts text using OCR
    3. Identifies medical entities using BiomedNER
    4. Structures the medication data
    5. Stores in database

    Returns:
        MedicationResponse with extracted medication details
    """
    try:
        # Get storage service
        storage_service = get_storage_service()

        # Upload image to local storage
        file_path = f"medications/{current_user['id']}/{image.filename}"

        file_content = await image.read()
        logger.info(f"Processing medication image: {file_path}")

        # Upload to storage
        public_url = await storage_service.upload_file(
            file_content, file_path, image.content_type
        )

        # Step 1: Extract text with OCR
        logger.info("Extracting text with OCR...")
        ocr_text = ocr_client.read_text(file_content)
        logger.info(f"OCR extracted text (length: {len(ocr_text)})")

        # Step 2: Extract medical entities with NER
        logger.info("Extracting medical entities with BiomedNER...")
        try:
            entities = ner_client.extract_entities(ocr_text)
            logger.info(f"NER extracted {len(entities)} entities")
        except Exception as ner_error:
            logger.warning(f"NER extraction failed: {ner_error}. Continuing without NER data.")
            entities = []

        # Step 3: Process and structure medication data
        title, active_ingredients, dosage, prescription_details = process_medication_text(
            ocr_text, entities
        )

        logger.info(
            f"Processed medication - Title: {title}, "
            f"Ingredients: {active_ingredients}, Dosage: {dosage}"
        )

        # Create medication record with structured data
        medication_data = MedicationCreate(
            profile_id=current_user["id"],
            scan_url=public_url,
            scanned_text=ocr_text,
            title=title,
            active_ingredients=active_ingredients,
            dosage=dosage,
            prescription_details=prescription_details,
        )

        medication = Medication(**medication_data.model_dump())
        db.add(medication)
        db.commit()
        db.refresh(medication)

        logger.info(f"Successfully created medication record with ID: {medication.id}")
        return MedicationResponse.model_validate(medication)

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Failed to process medication: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process medication image. Please try again.",
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
