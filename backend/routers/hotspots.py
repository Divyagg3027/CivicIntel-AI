"""
Hotspot Intelligence API Router
Exposes calculated Development Hotspots and detailed location profiles.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import schemas
from services.hotspot_service import calculate_hotspots

router = APIRouter(prefix="/hotspots", tags=["Hotspot Intelligence"])


@router.get("", response_model=List[schemas.HotspotResponse])
def get_all_hotspots(db: Session = Depends(get_db)):
    """
    Returns development hotspots aggregated by location and ranked by Civic Need Index (0-100).
    Synthesizes citizen requests, reported affected population, severity, infrastructure deficits,
    and public investment mitigation context.
    """
    hotspots = calculate_hotspots(db)
    return hotspots


@router.get("/{location}", response_model=schemas.HotspotResponse)
def get_hotspot_by_location(location: str, db: Session = Depends(get_db)):
    """
    Returns in-depth intelligence profile for a specific location hotspot.
    """
    hotspots = calculate_hotspots(db)
    target = location.strip().lower()

    for h in hotspots:
        if h["location"].lower() == target:
            return h

    raise HTTPException(status_code=404, detail=f"Hotspot profile for '{location}' not found.")
