"""
Central Analysis Engine for CivicIntel AI
Converts unstructured citizen requests into structured intelligence:
- Language Detection
- Category Classification (Multilingual with scoring)
- Severity Scoring (High / Medium / Low)
- Affected People Extraction (Context-aware regex)
- Development Need Mapping
- Location Geocoding (Demo coordinates)
"""

import re
from typing import Dict, Any, Tuple, Optional
from services.language_service import detect_language

# Known demo coordinates
DEMO_COORDINATES: Dict[str, Tuple[float, float]] = {
    "nagercoil": (8.1833, 77.4119),
    "coimbatore": (11.0168, 76.9558),
    "madurai": (9.9252, 78.1198),
    "chennai": (13.0827, 80.2707),
    "tirunelveli": (8.7139, 77.7567),
    "salem": (11.6643, 78.1460),
    "trichy": (10.7905, 78.7047),
    "tiruchirappalli": (10.7905, 78.7047),
    "thoothukudi": (8.7642, 78.1348),
    "tuticorin": (8.7642, 78.1348),
}

# Category to Development Need Mapping
DEVELOPMENT_NEEDS: Dict[str, str] = {
    "Water": "Drinking Water Infrastructure",
    "Roads": "Road Repair / Road Infrastructure",
    "Electricity": "Electricity Infrastructure",
    "Healthcare": "Healthcare Access",
    "Education": "Education Infrastructure",
    "Sanitation": "Sanitation Infrastructure",
    "Waste Management": "Waste Collection / Waste Management",
    "Public Transport": "Public Transport Connectivity",
    "Housing": "Housing / Infrastructure Assistance",
    "Other": "Civic Support & Services",
}

# Multilingual Category Vocabularies with weights
CATEGORY_KEYWORDS: Dict[str, Dict[str, int]] = {
    "Water": {
        # English
        "drinking water": 5, "water supply": 5, "tap water": 4, "borewell": 4,
        "water shortage": 4, "no water": 4, "contaminated water": 4, "pipeline leak": 3,
        "water": 2, "pipeline": 2, "well": 2, "drain water mixing": 3,
        # Tamil
        "குடிநீர்": 5, "தண்ணீர்": 4, "நீர்": 3, "குழாய்": 3, "ஆழ்குழாய்": 4, "நீர் தட்டுப்பாடு": 5,
        # Hindi
        "पीने का पानी": 5, "पानी": 3, "जल आपूर्ति": 5, "नल का पानी": 4, "जल": 3,
        # Telugu
        "మంచి నీరు": 5, "తాగునీరు": 5, "నీరు": 3, "నీటి కొరత": 5,
        # Malayalam
        "കുടിവെള്ളം": 5, "വെള്ളം": 3, "ജലവിതരണം": 5,
        # Kannada
        "ಕುಡಿಯುವ ನೀರು": 5, "ನೀರು": 3, "ನೀರಿನ ಕೊರತೆ": 5,
    },
    "Roads": {
        # English
        "pothole": 4, "potholes": 4, "damaged road": 5, "broken road": 4,
        "road repair": 4, "tar road": 3, "street condition": 3, "road": 2,
        "highway": 2, "bridge": 3, "flyover": 3, "traffic signal": 2,
        # Tamil
        "சாலை": 4, "ரோடு": 3, "பள்ளம்": 4, "குண்டும் குழியும்": 5, "சாலை சேதம்": 5, "பாலம்": 3,
        # Hindi
        "सड़क": 4, "गड्ढे": 4, "टूटी सड़क": 5, "मार्ग": 3, "पुल": 3,
        # Telugu
        "రోడ్డు": 4, "గుంతలు": 4, "పాడైన రోడ్డు": 5,
        # Malayalam
        "റോഡ്": 4, "കുഴികൾ": 4, "തകർന്ന റോഡ്": 5,
        # Kannada
        "ರಸ್ತೆ": 4, "ಗುಂಡಿಗಳು": 4, "ಹಾಳಾದ ರಸ್ತೆ": 5,
    },
    "Electricity": {
        # English
        "power cut": 5, "power outage": 5, "electricity supply": 5, "no electricity": 5,
        "low voltage": 4, "transformer": 4, "electric wire": 4, "street light": 4,
        "power": 2, "electricity": 3, "current": 2, "blackout": 4,
        # Tamil
        "மின்சாரம்": 4, "மின்வெட்டு": 5, "மின் கம்பி": 4, "தெருவிளக்கு": 4, "மின்மாற்றி": 4, "கரண்ட்": 3,
        # Hindi
        "बिजली": 4, "बिजली कटौती": 5, "विद्युत": 3, "ट्रांसफार्मर": 4, "स्ट्रीट लाइट": 4,
        # Telugu
        "విద్యుత్": 4, "కరెంట్ కోత": 5, "కరెంట్": 3, "వీధి దీపాలు": 4,
        # Malayalam
        "വൈദ്യുതി": 4, "വൈദ്യുതി മുടക്കം": 5, "സ്ട്രീറ്റ് ലൈറ്റ്": 4,
        # Kannada
        "ವಿದ್ಯುತ್": 4, "ಕರೆಂಟ್ ಕಟ್": 5, "ಬೀದಿ ದೀಪ": 4,
    },
    "Healthcare": {
        # English
        "hospital": 5, "primary health centre": 5, "phc": 4, "clinic": 4,
        "doctor": 4, "ambulance": 4, "medicine": 3, "healthcare": 4,
        "medical center": 4, "dispensary": 4, "emergency care": 4,
        # Tamil
        "மருத்துவமனை": 5, "சுகாதாரம்": 4, "மருத்துவர்": 4, "ஆம்புலன்ஸ்": 4, "மருந்து": 3, "ஆரம்ப சுகாதார நிலையம்": 5,
        # Hindi
        "अस्पताल": 5, "स्वास्थ्य": 4, "डॉक्टर": 4, "दवा": 3, "चिकित्सा": 4, "एम्बुलेंस": 4,
        # Telugu
        "ఆసుపత్రి": 5, "వైద్యం": 4, "డాక్టర్": 4, "మందులు": 3, "ఆరోగ్యం": 4,
        # Malayalam
        "ആശുപത്രി": 5, "ഡോക്ടർ": 4, "ആരോഗ്യം": 4, "മരുന്ന്": 3,
        # Kannada
        "ಆಸ್ಪತ್ರೆ": 5, "ವೈದ್ಯರು": 4, "ಆರೋಗ್ಯ": 4, "ಔಷಧ": 3,
    },
    "Education": {
        # English
        "school": 5, "college": 4, "classroom": 4, "school building": 5,
        "teacher": 3, "desks": 3, "education": 4, "library": 3,
        # Tamil
        "பள்ளி": 5, "கல்லூரி": 4, "ஆசிரியர்": 3, "வகுப்பறை": 4, "கல்வி": 4, "பள்ளிக்கூடம்": 5,
        # Hindi
        "स्कूल": 5, "विद्यालय": 5, "शिक्षक": 3, "कक्षा": 4, "शिक्षा": 4,
        # Telugu
        "పాఠశాల": 5, "బడి": 4, "ఉపాధ్యాయుడు": 3, "తరగతి గది": 4, "విద్య": 4,
        # Malayalam
        "സ്കൂൾ": 5, "വിദ്യാലയം": 5, "അധ്യാപകൻ": 3, "വിദ്യാഭ്യാസം": 4,
        # Kannada
        "ಶಾಲೆ": 5, "ಶಿಕ್ಷಕ": 3, "ತರಗತಿ": 4, "ಶಿಕ್ಷಣ": 4,
    },
    "Sanitation": {
        # English
        "drainage": 5, "sewer": 5, "sewage": 5, "toilet": 4, "public toilet": 5,
        "gutter": 4, "open drain": 5, "sanitation": 4, "drain overflow": 5,
        # Tamil
        "சாக்கடை": 5, "கழிவுநீர்": 5, "கழிப்பறை": 5, "வடிகால்": 4, "பொது கழிப்பிடம்": 5,
        # Hindi
        "नाली": 5, "सीवर": 5, "शौचालय": 5, "स्वच्छता": 4, "गंदा पानी": 4,
        # Telugu
        "డ్రైనేజీ": 5, "మురుగునీరు": 5, "మరుగుదొడ్డి": 5, "కాలువ": 4,
        # Malayalam
        "ഓട": 5, "മലിനജലം": 5, "ശൗചാലയം": 5,
        # Kannada
        "ಚರಂಡಿ": 5, "ತ್ಯಾಜ್ಯ ನೀರು": 5, "ಶೌಚಾಲಯ": 5,
    },
    "Waste Management": {
        # English
        "garbage": 5, "trash": 4, "waste": 4, "dump yard": 5, "garbage collection": 5,
        "waste disposal": 5, "litter": 3, "rubbish": 4, "plastic waste": 3,
        # Tamil
        "குப்பை": 5, "குப்பைக் கூடை": 4, "கழிவு": 3, "குப்பை கிடங்கு": 5, "குப்பை அகற்றல்": 5,
        # Hindi
        "कचरा": 5, "कूड़ा": 5, "कूड़ेदान": 4, "अपशिष्ट प्रबंधन": 5,
        # Telugu
        "చెత్త": 5, "వ్యర్థాలు": 4, "చెత్తకుండీ": 4,
        # Malayalam
        "മാലിന്യം": 5, "ചവറ്": 5, "മാലിന്യ സംസ്കരണം": 5,
        # Kannada
        "ಕಸ": 5, "ತ್ಯಾಜ್ಯ": 4, "ಕಸದ ತೊಟ್ಟಿ": 4,
    },
    "Public Transport": {
        # English
        "bus": 4, "bus stop": 5, "bus frequency": 5, "public transport": 5,
        "train": 3, "metro": 3, "transport": 3, "commute": 3,
        # Tamil
        "பேருந்து": 5, "பஸ்": 4, "பேருந்து நிறுத்தம்": 5, "போக்குவரத்து": 4,
        # Hindi
        "बस": 4, "बस स्टैंड": 5, "सार्वजनिक परिवहन": 5, "परिवहन": 4,
        # Telugu
        "బస్సు": 4, "బస్ స్టాండ్": 5, "రవాణా": 4,
        # Malayalam
        "ബസ്": 4, "ബസ് സ്റ്റോപ്പ്": 5, "ഗതാഗതം": 4,
        # Kannada
        "ಬಸ್": 4, "ಬಸ್ ನಿಲ್ದಾಣ": 5, "ಸಾರಿಗೆ": 4,
    },
    "Housing": {
        # English
        "housing": 5, "slum": 4, "shelter": 4, "encroachment": 3, "roof": 3, "homeless": 4,
        # Tamil
        "வீடு": 4, "குடிசை": 4, "இருப்பிடம்": 4,
        # Hindi
        "आवास": 5, "मकान": 4, "बस्ती": 3, "आश्रय": 4,
        # Telugu
        "ఇల్లు": 4, "గృహనిర్మాణం": 5, "నివాసం": 4,
        # Malayalam
        "ഭവനം": 5, "വീട്": 4, "പാർപ്പിടം": 4,
        # Kannada
        "ಮನೆ": 4, "ವಸತಿ": 5,
    },
}

# High Severity Keywords with weights
HIGH_SEVERITY_KEYWORDS = {
    # English
    "urgent": 3, "emergency": 4, "danger": 4, "dangerous": 4, "critical": 4,
    "unsafe": 3, "accident": 4, "death": 5, "completely unavailable": 4, "no drinking water": 4,
    "no water": 3, "no electricity": 3, "severe": 3, "life threatening": 5,
    "hazard": 3, "crisis": 4, "acute": 3, "collapsed": 4,
    # Tamil
    "இல்லை": 3, "அவசரம்": 4, "ஆபத்து": 4, "அவசரநிலை": 4, "உயிருக்கு ஆபத்து": 5,
    "விபத்து": 4, "மோசமான நிலை": 3, "முற்றிலும் இல்லை": 4,
    # Hindi
    "आपातकाल": 4, "खतरा": 4, "मृत्यु": 5, "अति आवश्यक": 4, "नहीं है": 3,
    # Telugu
    "అత్యవసరం": 4, "ప్రమాదం": 4, "లేదు": 3,
    # Malayalam
    "അടിയന്തിരം": 4, "അപകടം": 4, "ഇല്ല": 3,
    # Kannada
    "ತುರ್ತು": 4, "ಅಪಾಯ": 4, "ಇಲ್ಲ": 3,
}

# Medium Severity Keywords with weights
MEDIUM_SEVERITY_KEYWORDS = {
    # English
    "problem": 2, "poor": 2, "damaged": 2, "damage": 2, "shortage": 2,
    "frequent": 2, "issue": 1, "bad": 2, "broken": 2, "pothole": 2, "potholes": 2,
    "leakage": 2, "irregular": 2, "struggling": 2, "delay": 1, "dirty": 2,
    # Tamil
    "பிரச்சனை": 2, "மோசம்": 2, "சேதம்": 2, "பழுது": 2, "குறைபாடு": 2, "தடை": 1,
    # Hindi
    "समस्या": 2, "खराब": 2, "कमी": 2, "टूटा": 2, "परेशानी": 2,
    # Telugu
    "సమస్య": 2, "చెడిపోయింది": 2, "కొరత": 2,
    # Malayalam
    "പ്രശ്നം": 2, "കേടുപാടുകൾ": 2, "ബുദ്ധിമുട്ട്": 2,
    # Kannada
    "ಸಮಸ್ಯೆ": 2, "ಹಾಳಾಗಿದೆ": 2, "ತೊಂದರೆ": 2,
}


def extract_affected_people(text: str) -> int:
    """
    Extracts the estimated number of affected people from context words.
    Looks for numbers associated with people, families, residents, households, etc.
    Avoids interpreting dates, times, or ward numbers as affected people.
    """
    if not text:
        return 0

    clean_text = text.strip()

    # Pre-cleaning: remove ward/route/year patterns so they don't get misidentified
    # e.g., "ward 12", "bus 45A", "year 2024"
    masked_text = re.sub(r'(?i)\b(ward|route|bus|pincode|pin|sector|phase|year)\s*#?\d+', ' ', clean_text)

    # Patterns where number precedes the contextual word
    # e.g. "500 people", "around 300 families", "nearly 200 residents", "500 மக்கள்"
    patterns_before = [
        # English
        r'(?:around|about|nearly|approximately|over|more than)?\s*(\d{1,7})\s*(?:people|persons|residents|citizens|families|households|students|workers|commuters|villagers|patients)\b',
        r'affecting\s*(?:around|about|nearly|approximately|over)?\s*(\d{1,7})',
        r'(\d{1,7})\s*(?:people|residents|families|households|citizens)\s*(?:are|have been|were)?\s*affected',
        # Tamil
        r'(\d{1,7})\s*(?:பேர்|மக்கள்|குடும்பங்கள்|குடிமக்கள்|மாணவர்கள்|தொழிலாளர்கள்)',
        r'(\d{1,7})\s*மக்கள்\s*பாதிக்கப்பட்டுள்ளனர்',
        r'(\d{1,7})\s*குடும்பங்கள்\s*பாதிக்கப்பட்டுள்ளன',
        # Hindi
        r'(\d{1,7})\s*(?:लोग|परिवार|नागरिक|छात्र|मरीज)',
        # Telugu
        r'(\d{1,7})\s*(?:మంది|ప్రజలు|కుటుంబాలు)',
        # Malayalam
        r'(\d{1,7})\s*(?:ആളുകൾ|കുടുംബങ്ങൾ|പേർ)',
        # Kannada
        r'(\d{1,7})\s*(?:ಜನರು|ಕುಟುಂಬಗಳು)',
    ]

    for pat in patterns_before:
        m = re.search(pat, masked_text, re.IGNORECASE)
        if m:
            try:
                val = int(m.group(1))
                if 1 <= val <= 5000000:
                    return val
            except (ValueError, IndexError):
                pass

    # Patterns where contextual word precedes number
    # e.g. "affected people: 500", "affected: 200", "population of 400"
    patterns_after = [
        r'(?:affected\s*(?:people|citizens|families|population)?|affected)\s*[:=-]?\s*(\d{1,7})',
        r'(?:பாதிக்கப்பட்ட\s*மக்கள்)\s*[:=-]?\s*(\d{1,7})',
    ]

    for pat in patterns_after:
        m = re.search(pat, masked_text, re.IGNORECASE)
        if m:
            try:
                val = int(m.group(1))
                if 1 <= val <= 5000000:
                    return val
            except (ValueError, IndexError):
                pass

    return 0


def detect_category(text: str) -> str:
    """
    Detects the civic category using weighted keyword and phrase scoring.
    """
    if not text:
        return "Other"

    text_lower = text.lower()
    scores: Dict[str, int] = {cat: 0 for cat in CATEGORY_KEYWORDS}

    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw, weight in keywords.items():
            if kw in text_lower:
                scores[cat] += weight

    best_cat = max(scores, key=scores.get)
    if scores[best_cat] > 0:
        return best_cat

    return "Other"


def detect_severity(text: str, category: str = "") -> str:
    """
    Detects severity (High, Medium, Low) using weighted rule-based classification.
    """
    if not text:
        return "Low"

    text_lower = text.lower()
    high_score = 0
    medium_score = 0

    for kw, weight in HIGH_SEVERITY_KEYWORDS.items():
        if kw in text_lower:
            high_score += weight

    for kw, weight in MEDIUM_SEVERITY_KEYWORDS.items():
        if kw in text_lower:
            medium_score += weight

    if high_score >= 3 or (high_score >= 2 and medium_score >= 2):
        return "High"
    elif high_score > 0 or medium_score >= 2:
        return "Medium"
    else:
        return "Low"


def get_coordinates(location: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Resolves demonstration coordinates for known locations.
    """
    if not location:
        return None, None

    loc_key = location.strip().lower()
    for name, coords in DEMO_COORDINATES.items():
        if name in loc_key:
            return coords[0], coords[1]

    # Default fallback near Tamil Nadu center
    return 10.7905, 78.7047


def analyze_request_data(text: str, location: str = "") -> Dict[str, Any]:
    """
    Central analysis function for all citizen requests.
    Standardized across all ingestion pathways.
    """
    language = detect_language(text)
    category = detect_category(text)
    severity = detect_severity(text, category=category)
    affected_people = extract_affected_people(text)
    detected_need = DEVELOPMENT_NEEDS.get(category, "Civic Support & Services")
    lat, lng = get_coordinates(location)

    return {
        "language": language,
        "category": category,
        "severity": severity,
        "affected_people": affected_people,
        "detected_need": detected_need,
        "latitude": lat,
        "longitude": lng,
    }
