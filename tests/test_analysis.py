"""
Automated Unit Tests for Analysis & NLP Engine
Tests:
- Category Classification (Multilingual)
- Severity Scoring (High / Medium / Low)
- Affected People Contextual Extraction
- Language Detection (Unicode script analysis)
- Standardized Acceptance Scenarios
"""

import pytest
import sys
from pathlib import Path

# Add backend directory to sys.path
BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from services.language_service import detect_language
from services.analysis_service import (
    analyze_request_data,
    detect_category,
    detect_severity,
    extract_affected_people,
)


def test_language_detection():
    # English
    assert detect_language("No drinking water in our area.") == "English"
    # Tamil
    assert detect_language("எங்கள் பகுதியில் குடிநீர் இல்லை") == "Tamil"
    # Hindi
    assert detect_language("हमारे गांव में बिजली नहीं है") == "Hindi"
    # Telugu
    assert detect_language("మా గ్రామంలో నీటి కొరత ఉంది") == "Telugu"
    # Malayalam
    assert detect_language("ഞങ്ങളുടെ പ്രദേശത്ത് കുടിവെള്ളമില്ല") == "Malayalam"
    # Kannada
    assert detect_language("ನಮ್ಮ ಪ್ರದೇಶದಲ್ಲಿ ಕುಡಿಯುವ ನೀರಿನ ಸಮಸ್ಯೆ ಇದೆ") == "Kannada"


def test_category_detection():
    assert detect_category("We need drinking water pipeline connection") == "Water"
    assert detect_category("Deep potholes have damaged the main street") == "Roads"
    assert detect_category("Frequent power cuts and low voltage") == "Electricity"
    assert detect_category("Primary health centre needs an ambulance and doctor") == "Healthcare"
    assert detect_category("School building roof is leaking") == "Education"
    assert detect_category("Open drainage overflowing into residential area") == "Sanitation"
    assert detect_category("Garbage has not been collected for a week") == "Waste Management"
    assert detect_category("Bus frequency is too low during morning commute") == "Public Transport"


def test_multilingual_category_detection():
    # Tamil
    assert detect_category("எங்கள் பகுதியில் குடிநீர் தட்டுப்பாடு உள்ளது") == "Water"
    assert detect_category("சாலை மிகவும் மோசமாக சேதமடைந்துள்ளது") == "Roads"
    assert detect_category("மின்வெட்டு பிரச்சனை தொடர்கிறது") == "Electricity"
    # Hindi
    assert detect_category("पीने के पानी की सख्त जरूरत है") == "Water"
    assert detect_category("सड़क पर बहुत गड्ढे हैं") == "Roads"


def test_severity_detection():
    # High
    assert detect_severity("Urgent emergency, open live wire dangerous for pedestrians") == "High"
    assert detect_severity("எங்கள் பகுதியில் குடிநீர் இல்லை, அவசர நிலை") == "High"
    # Medium
    assert detect_severity("Road surface is slightly damaged and has small potholes") == "Medium"
    # Low
    assert detect_severity("Please consider planting trees along the boulevard") == "Low"


def test_affected_people_extraction():
    assert extract_affected_people("Around 500 people are affected by water shortage") == 500
    assert extract_affected_people("Over 300 families have no electricity") == 300
    assert extract_affected_people("200 residents are facing daily traffic delays") == 200
    assert extract_affected_people("500 மக்கள் பாதிக்கப்பட்டுள்ளனர்") == 500
    assert extract_affected_people("300 குடும்பங்கள் அவதி") == 300
    # Guard against non-affected numbers
    assert extract_affected_people("Meeting at ward 12 regarding bus 45A in year 2024") == 0


def test_acceptance_criteria_1():
    # "There is no drinking water in our village. Around 500 people are affected."
    res = analyze_request_data(
        "There is no drinking water in our village. Around 500 people are affected.",
        "Nagercoil"
    )
    assert res["language"] == "English"
    assert res["category"] == "Water"
    assert res["severity"] == "High"
    assert res["affected_people"] == 500
    assert res["detected_need"] == "Drinking Water Infrastructure"


def test_acceptance_criteria_2():
    # "Many potholes have damaged our road and around 200 residents are affected."
    res = analyze_request_data(
        "Many potholes have damaged our road and around 200 residents are affected.",
        "Coimbatore"
    )
    assert res["category"] == "Roads"
    assert res["affected_people"] == 200


def test_acceptance_criteria_3():
    # "எங்கள் பகுதியில் குடிநீர் இல்லை. 500 மக்கள் பாதிக்கப்பட்டுள்ளனர்."
    res = analyze_request_data(
        "எங்கள் பகுதியில் குடிநீர் இல்லை. 500 மக்கள் பாதிக்கப்பட்டுள்ளனர்.",
        "Madurai"
    )
    assert res["language"] == "Tamil"
    assert res["category"] == "Water"
    assert res["severity"] == "High"
    assert res["affected_people"] == 500
