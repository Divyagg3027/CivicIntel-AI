"""
Citizen Requests API Router
Handles ingestion, filtering, retrieval, and re-analysis of civic requests.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from database import get_db
import models
import schemas
from services.analysis_service import analyze_request_data

router = APIRouter(prefix="/requests", tags=["Citizen Requests"])


@router.post("", response_model=schemas.CitizenRequestCreateResponse, status_code=status.HTTP_201_CREATED)
def create_citizen_request(
    payload: schemas.CitizenRequestCreate,
    db: Session = Depends(get_db)
):
    """
    Submits a new citizen request:
    1. Validates input
    2. Runs central AI/NLP analysis (Category, Severity, Language, Affected People, Detected Need, Geocoding)
    3. Persists record in MySQL
    4. Returns structured intelligence
    """
    text = payload.request_text.strip()
    loc = payload.location.strip()

    if not text or len(text) < 3:
        raise HTTPException(status_code=400, detail="Request description must contain at least 3 characters.")
    if not loc or len(loc) < 2:
        raise HTTPException(status_code=400, detail="Location must contain at least 2 characters.")

    # Central analysis engine
    analysis = analyze_request_data(text, loc)

    new_request = models.CitizenRequest(
        request_text=text,
        location=loc,
        latitude=analysis.get("latitude"),
        longitude=analysis.get("longitude"),
        language=analysis.get("language", "English"),
        category=analysis.get("category", "Other"),
        severity=analysis.get("severity", "Low"),
        affected_people=analysis.get("affected_people", 0),
        detected_need=analysis.get("detected_need", "Civic Support & Services"),
        status="Analyzed"
    )

    db.add(new_request)
    db.commit()
    db.refresh(new_request)

    return {
        "message": "Citizen request successfully processed and analyzed into civic intelligence!",
        "request": new_request
    }


@router.get("", response_model=List[schemas.CitizenRequestOut])
def get_citizen_requests(
    search: Optional[str] = Query(None, description="Search request text"),
    category: Optional[str] = Query(None, description="Filter by category"),
    severity: Optional[str] = Query(None, description="Filter by severity (High, Medium, Low)"),
    language: Optional[str] = Query(None, description="Filter by language"),
    location: Optional[str] = Query(None, description="Filter by location"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by processing status"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Retrieves filtered citizen requests.
    Supports multi-criteria querying across category, severity, language, location, and search text.
    """
    query = db.query(models.CitizenRequest)

    if search:
        search_pattern = f"%{search.strip()}%"
        query = query.filter(models.CitizenRequest.request_text.ilike(search_pattern))

    if category and category.lower() != "all":
        query = query.filter(models.CitizenRequest.category == category)

    if severity and severity.lower() != "all":
        query = query.filter(models.CitizenRequest.severity == severity)

    if language and language.lower() != "all":
        query = query.filter(models.CitizenRequest.language == language)

    if location and location.lower() != "all":
        query = query.filter(models.CitizenRequest.location.ilike(f"%{location.strip()}%"))

    if status_filter:
        query = query.filter(models.CitizenRequest.status == status_filter)

    requests = query.order_by(models.CitizenRequest.id.desc()).offset(offset).limit(limit).all()
    return requests


@router.get("/{request_id}", response_model=schemas.CitizenRequestOut)
def get_citizen_request_by_id(
    request_id: int,
    db: Session = Depends(get_db)
):
    """
    Fetches full detail for a single citizen request.
    """
    req = db.query(models.CitizenRequest).filter(models.CitizenRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail=f"Citizen request #{request_id} not found.")
    return req


@router.post("/{request_id}/analyze", response_model=schemas.CitizenRequestOut)
def reanalyze_citizen_request(
    request_id: int,
    db: Session = Depends(get_db)
):
    """
    Re-runs the central analysis engine on an existing request.
    """
    req = db.query(models.CitizenRequest).filter(models.CitizenRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail=f"Citizen request #{request_id} not found.")

    analysis = analyze_request_data(req.request_text, req.location)
    req.language = analysis["language"]
    req.category = analysis["category"]
    req.severity = analysis["severity"]
    req.affected_people = analysis["affected_people"]
    req.detected_need = analysis["detected_need"]
    req.latitude = analysis["latitude"]
    req.longitude = analysis["longitude"]
    req.status = "Analyzed"

    db.commit()
    db.refresh(req)
    return req
