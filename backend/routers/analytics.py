"""
Analytics API Router
Provides aggregated civic metrics computed from actual database data:
- Summary KPI Cards
- Category Distribution
- Language Breakdown
- Location Aggregates
- Comparative Infrastructure vs Reported Need vs Investment Intelligence
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
import models
import schemas

router = APIRouter(prefix="/analytics", tags=["Civic Analytics"])


@router.get("/summary", response_model=schemas.SummaryAnalytics)
def get_analytics_summary(db: Session = Depends(get_db)):
    """
    Returns high-level summary KPIs derived from live MySQL database records.
    """
    total_requests = db.query(func.count(models.CitizenRequest.id)).scalar() or 0
    high_severity = db.query(func.count(models.CitizenRequest.id)).filter(models.CitizenRequest.severity == "High").scalar() or 0
    medium_severity = db.query(func.count(models.CitizenRequest.id)).filter(models.CitizenRequest.severity == "Medium").scalar() or 0
    low_severity = db.query(func.count(models.CitizenRequest.id)).filter(models.CitizenRequest.severity == "Low").scalar() or 0
    total_affected = db.query(func.sum(models.CitizenRequest.affected_people)).scalar() or 0
    hotspot_count = db.query(func.count(models.HotspotAnalysis.id)).filter(models.HotspotAnalysis.civic_need_index >= 60.0).scalar() or 0

    return {
        "total_requests": int(total_requests),
        "high_severity": int(high_severity),
        "medium_severity": int(medium_severity),
        "low_severity": int(low_severity),
        "total_affected_people": int(total_affected),
        "hotspot_count": int(hotspot_count),
    }


@router.get("/categories", response_model=List[schemas.CategoryItem])
def get_analytics_categories(db: Session = Depends(get_db)):
    """
    Returns distribution of citizen requests grouped by category.
    """
    total = db.query(func.count(models.CitizenRequest.id)).scalar() or 0

    results = (
        db.query(models.CitizenRequest.category, func.count(models.CitizenRequest.id).label("cnt"))
        .group_by(models.CitizenRequest.category)
        .order_by(func.count(models.CitizenRequest.id).desc())
        .all()
    )

    items = []
    for cat, cnt in results:
        category_name = cat or "Other"
        pct = round((cnt / total * 100.0), 1) if total > 0 else 0.0
        items.append({
            "category": category_name,
            "count": cnt,
            "percentage": pct
        })
    return items


@router.get("/languages", response_model=List[schemas.LanguageItem])
def get_analytics_languages(db: Session = Depends(get_db)):
    """
    Returns breakdown of citizen requests by detected language.
    """
    total = db.query(func.count(models.CitizenRequest.id)).scalar() or 0

    results = (
        db.query(models.CitizenRequest.language, func.count(models.CitizenRequest.id).label("cnt"))
        .group_by(models.CitizenRequest.language)
        .order_by(func.count(models.CitizenRequest.id).desc())
        .all()
    )

    items = []
    for lang, cnt in results:
        language_name = lang or "English"
        pct = round((cnt / total * 100.0), 1) if total > 0 else 0.0
        items.append({
            "language": language_name,
            "count": cnt,
            "percentage": pct
        })
    return items


@router.get("/locations", response_model=List[schemas.LocationItem])
def get_analytics_locations(db: Session = Depends(get_db)):
    """
    Returns citizen requests grouped by location with total affected count and dominant need.
    """
    loc_stats = (
        db.query(
            models.CitizenRequest.location,
            func.count(models.CitizenRequest.id).label("cnt"),
            func.sum(models.CitizenRequest.affected_people).label("affected")
        )
        .group_by(models.CitizenRequest.location)
        .order_by(func.count(models.CitizenRequest.id).desc())
        .all()
    )

    items = []
    for loc, cnt, aff in loc_stats:
        # Find dominant category for this location
        dom = (
            db.query(models.CitizenRequest.category)
            .filter(models.CitizenRequest.location == loc)
            .group_by(models.CitizenRequest.category)
            .order_by(func.count(models.CitizenRequest.id).desc())
            .first()
        )
        dominant_cat = dom[0] if dom else "Water"

        items.append({
            "location": loc,
            "count": cnt,
            "affected_people": int(aff or 0),
            "dominant_category": dominant_cat
        })

    return items


@router.get("/comparison")
def get_infrastructure_comparison(db: Session = Depends(get_db)):
    """
    Comparative Intelligence Endpoint:
    Compares Reported Citizen Need Index vs Demonstration Infrastructure Score vs Public Investment Context.
    """
    # Group by category across the whole state / dataset
    categories = ["Water", "Roads", "Electricity", "Healthcare", "Sanitation", "Waste Management", "Education", "Public Transport"]

    total_requests = db.query(func.count(models.CitizenRequest.id)).scalar() or 1

    comparison_data = []
    for cat in categories:
        # 1. Reported need intensity (normalized 0-100)
        req_cnt = db.query(func.count(models.CitizenRequest.id)).filter(models.CitizenRequest.category == cat).scalar() or 0
        need_score = min(100.0, round((req_cnt / total_requests) * 250.0, 1))

        # 2. Demonstration infrastructure score (average across locations)
        avg_infra = db.query(func.avg(models.InfrastructureData.infrastructure_score)).filter(models.InfrastructureData.category == cat).scalar()
        infra_score = round(float(avg_infra), 1) if avg_infra is not None else 50.0

        # 3. Demonstration investment context (normalized 0-100)
        total_inv = db.query(func.sum(models.InvestmentData.investment_amount)).filter(models.InvestmentData.category == cat).scalar()
        inv_val = float(total_inv) if total_inv is not None else 0.0
        # Normalize: 100 Cr corresponds to 100 score
        inv_score = min(100.0, round((inv_val / 200000000.0) * 100.0, 1))

        comparison_data.append({
            "category": cat,
            "reported_need_score": need_score,
            "infrastructure_score": infra_score,
            "investment_score": inv_score,
            "investment_amount": inv_val,
            "request_count": req_cnt
        })

    return {
        "disclaimer": "Development-gap indicators are analytical outputs generated from citizen requests and demonstration datasets. They are not official government assessments.",
        "comparison": comparison_data
    }
