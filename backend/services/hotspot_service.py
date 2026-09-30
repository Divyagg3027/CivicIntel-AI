"""
Hotspot Calculation & Aggregation Service
Calculates the Civic Need Index (0-100) combining:
1. Citizen Request Intensity
2. Reported Affected Population
3. Request Severity Score
4. Infrastructure Baseline Deficit
5. Public Investment Mitigation Discount
"""

import math
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, case
import models
from services.analysis_service import get_coordinates
from services.insight_service import generate_hotspot_insight


def calculate_hotspots(db: Session) -> List[Dict[str, Any]]:
    """
    Computes Civic Need Index for each location with requests or demo data.
    Updates the HotspotAnalysis table and returns ranked hotspots.
    """
    # 1. Aggregate requests by location
    request_stats = (
        db.query(
            models.CitizenRequest.location,
            func.count(models.CitizenRequest.id).label("request_count"),
            func.sum(models.CitizenRequest.affected_people).label("total_affected"),
            func.sum(
                case(
                    (models.CitizenRequest.severity == "High", 1.0),
                    (models.CitizenRequest.severity == "Medium", 0.5),
                    else_=0.2
                )
            ).label("severity_sum")
        )
        .group_by(models.CitizenRequest.location)
        .all()
    )

    req_by_loc = {}
    for r in request_stats:
        loc = r[0]
        req_by_loc[loc] = {
            "count": r[1] or 0,
            "affected": int(r[2] or 0),
            "severity_sum": float(r[3] or 0.0),
        }

    # 2. Get category breakdowns per location
    cat_stats = (
        db.query(
            models.CitizenRequest.location,
            models.CitizenRequest.category,
            func.count(models.CitizenRequest.id)
        )
        .group_by(models.CitizenRequest.location, models.CitizenRequest.category)
        .all()
    )

    cat_by_loc: Dict[str, Dict[str, int]] = {}
    for loc, cat, cnt in cat_stats:
        if loc not in cat_by_loc:
            cat_by_loc[loc] = {}
        cat_by_loc[loc][cat or "Other"] = cnt

    # 3. Retrieve population data
    pop_records = db.query(models.PopulationData).all()
    pop_by_loc = {p.location: p.population for p in pop_records}

    # 4. Retrieve infrastructure data
    infra_records = db.query(models.InfrastructureData).all()
    infra_by_loc: Dict[str, List[float]] = {}
    for inf in infra_records:
        if inf.location not in infra_by_loc:
            infra_by_loc[inf.location] = []
        infra_by_loc[inf.location].append(inf.infrastructure_score)

    # 5. Retrieve investment data
    inv_records = db.query(models.InvestmentData).all()
    inv_by_loc: Dict[str, float] = {}
    for inv in inv_records:
        inv_by_loc[inv.location] = inv_by_loc.get(inv.location, 0.0) + inv.investment_amount

    # Collect all locations to evaluate
    all_locations = set(req_by_loc.keys()) | set(pop_by_loc.keys()) | set(infra_by_loc.keys())

    results: List[Dict[str, Any]] = []

    for loc in all_locations:
        req_data = req_by_loc.get(loc, {"count": 0, "affected": 0, "severity_sum": 0.0})
        req_count = req_data["count"]
        affected_people = req_data["affected"]
        sev_sum = req_data["severity_sum"]

        # If zero requests and no demo presence, skip
        if req_count == 0 and loc not in pop_by_loc:
            continue

        population = pop_by_loc.get(loc, 250000)

        # Dominant category
        breakdown = cat_by_loc.get(loc, {})
        if breakdown:
            dominant_category = max(breakdown, key=breakdown.get)
        else:
            dominant_category = "Water"

        # Infrastructure score and gap
        loc_scores = infra_by_loc.get(loc, [])
        if loc_scores:
            avg_infra_score = sum(loc_scores) / len(loc_scores)
        else:
            avg_infra_score = 50.0  # Synthetic default midpoint
        infra_gap = max(0.0, 100.0 - avg_infra_score)

        # Investment amount
        total_inv = inv_by_loc.get(loc, 10000000.0)

        # --- Civic Need Index Calculation (0 to 100) ---
        # 1. Request Intensity Component (0 - 25 pts)
        if req_count > 0:
            req_rate = (req_count / population) * 10000.0
            i_req = min(25.0, (req_rate * 2.5) + min(12.0, req_count * 0.8))
        else:
            i_req = 0.0

        # 2. Affected Population Impact (0 - 25 pts)
        if affected_people > 0:
            pop_ratio = affected_people / max(population, 1)
            log_factor = math.log10(max(affected_people, 1)) * 3.0
            i_pop = min(25.0, (pop_ratio * 150.0) + log_factor)
        else:
            i_pop = 0.0

        # 3. Severity Score Component (0 - 20 pts)
        if req_count > 0:
            avg_sev = sev_sum / req_count
            i_sev = avg_sev * 20.0
        else:
            i_sev = 5.0

        # 4. Infrastructure Baseline Deficit Component (0 - 20 pts)
        i_inf = (infra_gap / 100.0) * 20.0

        # 5. Investment Mitigation Discount (0 - 10 pts)
        inv_per_capita = total_inv / max(population, 1)
        i_inv = min(10.0, (inv_per_capita / 100.0) * 4.0)

        # Combined Index (Clamped 0 - 100)
        cni = max(0.0, min(100.0, i_req + i_pop + i_sev + i_inf - i_inv))
        cni = round(cni, 1)

        # Geocoding
        lat, lng = get_coordinates(loc)

        # Insight explanation
        explanation = generate_hotspot_insight(
            location=loc,
            civic_need_index=cni,
            request_count=req_count,
            affected_people=affected_people,
            dominant_category=dominant_category,
            severity_score=round(i_sev, 1),
            infrastructure_gap=round(infra_gap, 1),
            investment_amount=total_inv,
            category_breakdown=breakdown,
        )

        # Upsert into HotspotAnalysis database model
        existing = db.query(models.HotspotAnalysis).filter(models.HotspotAnalysis.location == loc).first()
        if existing:
            existing.civic_need_index = cni
            existing.request_count = req_count
            existing.affected_people = affected_people
            existing.severity_score = round(i_sev, 1)
            existing.infrastructure_gap = round(infra_gap, 1)
            existing.investment_context = round(total_inv, 2)
            existing.dominant_category = dominant_category
            existing.explanation = explanation
        else:
            hotspot_rec = models.HotspotAnalysis(
                location=loc,
                civic_need_index=cni,
                request_count=req_count,
                affected_people=affected_people,
                severity_score=round(i_sev, 1),
                infrastructure_gap=round(infra_gap, 1),
                investment_context=round(total_inv, 2),
                dominant_category=dominant_category,
                explanation=explanation
            )
            db.add(hotspot_rec)

        results.append({
            "location": loc,
            "civic_need_index": cni,
            "request_count": req_count,
            "affected_people": affected_people,
            "severity_score": round(i_sev, 1),
            "infrastructure_gap": round(infra_gap, 1),
            "investment_context": round(total_inv, 2),
            "dominant_category": dominant_category,
            "explanation": explanation,
            "latitude": lat,
            "longitude": lng,
            "category_breakdown": breakdown,
            "infrastructure_score": round(avg_infra_score, 1),
            "investment_amount": total_inv
        })

    db.commit()

    # Sort descending by Civic Need Index
    results.sort(key=lambda x: x["civic_need_index"], reverse=True)
    return results
