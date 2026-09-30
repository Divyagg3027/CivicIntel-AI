from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class CitizenRequestCreate(BaseModel):
    request_text: str = Field(..., min_length=3, description="Citizen problem description")
    location: str = Field(..., min_length=2, description="Location of problem")


class CitizenRequestOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    request_text: str
    location: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    language: Optional[str] = None
    category: Optional[str] = None
    severity: Optional[str] = None
    affected_people: Optional[int] = 0
    status: Optional[str] = None
    detected_need: Optional[str] = None
    created_at: Optional[datetime] = None


class CitizenRequestCreateResponse(BaseModel):
    message: str
    request: CitizenRequestOut


class SummaryAnalytics(BaseModel):
    total_requests: int
    high_severity: int
    medium_severity: int
    low_severity: int
    total_affected_people: int
    hotspot_count: int


class CategoryItem(BaseModel):
    category: str
    count: int
    percentage: float


class LanguageItem(BaseModel):
    language: str
    count: int
    percentage: float


class LocationItem(BaseModel):
    location: str
    count: int
    affected_people: int
    dominant_category: str


class HotspotResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    location: str
    civic_need_index: float
    request_count: int
    affected_people: int
    severity_score: float
    infrastructure_gap: float
    investment_context: float
    dominant_category: str
    explanation: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    category_breakdown: Optional[Dict[str, int]] = None
    infrastructure_score: Optional[float] = None
    investment_amount: Optional[float] = None
    calculated_at: Optional[datetime] = None
