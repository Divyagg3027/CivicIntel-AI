"""
Insight Generation Service for CivicIntel AI
Produces analytical explanations synthesizing:
- Citizen Request Patterns
- Dominant Category & Severity
- Demonstration Infrastructure Baseline
- Demonstration Investment Context

Operates deterministically by default without external dependencies or paid APIs.
Optionally integrates with external LLMs if EXTERNAL_LLM_API_KEY is configured.
"""

import os
from typing import Dict, Any, Optional


def generate_hotspot_insight(
    location: str,
    civic_need_index: float,
    request_count: int,
    affected_people: int,
    dominant_category: str,
    severity_score: float,
    infrastructure_gap: float,
    investment_amount: float,
    category_breakdown: Optional[Dict[str, int]] = None
) -> str:
    """
    Generates an analytical, grounded intelligence narrative.
    Strictly factual to the supplied structured metrics without fabricating data.
    """
    api_key = os.getenv("EXTERNAL_LLM_API_KEY", "").strip()

    if api_key:
        try:
            llm_text = _call_external_llm(
                location=location,
                civic_need_index=civic_need_index,
                request_count=request_count,
                affected_people=affected_people,
                dominant_category=dominant_category,
                infrastructure_gap=infrastructure_gap,
                investment_amount=investment_amount,
                api_key=api_key,
            )
            if llm_text:
                return llm_text
        except Exception:
            # Fall back safely to deterministic generator on any failure
            pass

    return _generate_deterministic_insight(
        location=location,
        civic_need_index=civic_need_index,
        request_count=request_count,
        affected_people=affected_people,
        dominant_category=dominant_category,
        severity_score=severity_score,
        infrastructure_gap=infrastructure_gap,
        investment_amount=investment_amount,
        category_breakdown=category_breakdown or {},
    )


def _generate_deterministic_insight(
    location: str,
    civic_need_index: float,
    request_count: int,
    affected_people: int,
    dominant_category: str,
    severity_score: float,
    infrastructure_gap: float,
    investment_amount: float,
    category_breakdown: Dict[str, int],
) -> str:
    """
    Deterministic rule-based intelligence generator.
    """
    # Severity assessment
    if severity_score >= 15:
        severity_desc = "critical severity with acute urgency"
    elif severity_score >= 10:
        severity_desc = "moderate-to-high severity"
    else:
        severity_desc = "predominantly routine or localized severity"

    # Infrastructure gap assessment
    if infrastructure_gap >= 55:
        infra_desc = "indicates a substantial deficit in municipal baseline coverage"
    elif infrastructure_gap >= 35:
        infra_desc = "shows moderate readiness with recognizable capacity constraints"
    else:
        infra_desc = "reflects relatively resilient existing physical infrastructure"

    # Investment context assessment
    if investment_amount > 50000000:
        inv_desc = f"substantial recent public investment (₹{investment_amount/10000000:.1f} Cr) is actively programmed"
    elif investment_amount > 10000000:
        inv_desc = f"moderate investment (₹{investment_amount/10000000:.1f} Cr) is recorded"
    else:
        inv_desc = f"limited recent public investment (₹{investment_amount/10000000:.1f} Cr) has been recorded"

    # Need priority level
    if civic_need_index >= 70:
        urgency_label = "Priority Tier 1 Hotspot"
        recommendation = f"Immediate cross-departmental intervention recommended for {dominant_category.lower()} modernization."
    elif civic_need_index >= 45:
        urgency_label = "Priority Tier 2 Need Zone"
        recommendation = f"Targeted capital allocation advised to reinforce {dominant_category.lower()} networks."
    else:
        urgency_label = "Monitoring & Maintenance Zone"
        recommendation = "Ongoing standard municipal maintenance and periodic surveillance sufficient."

    insight = (
        f"{location} is identified as a {urgency_label} with a Civic Need Index of {civic_need_index:.1f}/100. "
        f"Analysis of {request_count} verified citizen reports indicates an aggregate affected cohort of approximately "
        f"{affected_people:,} residents, with reports characterized by {severity_desc}. "
        f"The primary civic stressor is {dominant_category}, which accounts for the largest share of citizen distress. "
        f"In comparison, the demonstration infrastructure baseline {infra_desc} (gap index: {infrastructure_gap:.1f}/100), "
        f"while {inv_desc}. {recommendation}"
    )

    return insight


def _call_external_llm(
    location: str,
    civic_need_index: float,
    request_count: int,
    affected_people: int,
    dominant_category: str,
    infrastructure_gap: float,
    investment_amount: float,
    api_key: str,
) -> Optional[str]:
    """
    Optional external LLM caller (Gemini / OpenAI compatible API).
    Only used if API key is provided by the operator.
    """
    import httpx

    prompt = (
        f"You are CivicIntel AI's civic intelligence analyst. Write a concise 3-sentence development intelligence summary "
        f"strictly using these facts: Location: {location}, Civic Need Index: {civic_need_index:.1f}/100, "
        f"Citizen Requests: {request_count}, Affected Population: {affected_people}, "
        f"Dominant Category: {dominant_category}, Infrastructure Deficit Gap: {infrastructure_gap:.1f}/100, "
        f"Demo Investment: ₹{investment_amount/10000000:.1f} Cr. "
        f"Do not invent any facts. Ground the response in citizen reported needs and infrastructure context."
    )

    # Example endpoint implementation for Google Gemini API or OpenAI
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    resp = httpx.post(url, json=payload, timeout=8.0)
    if resp.status_code == 200:
        data = resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()

    return None
