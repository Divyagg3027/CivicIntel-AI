"""
Language Detection Service
Local, dependency-free language detection based on Unicode script block analysis
Supports English, Tamil, Hindi, Telugu, Malayalam, Kannada, and Other.
"""

import re
from typing import Dict

# Unicode Script Ranges
SCRIPT_RANGES = {
    "Tamil": (0x0B80, 0x0BFF),
    "Hindi": (0x0900, 0x097F),       # Devanagari
    "Telugu": (0x0C00, 0x0C7F),
    "Malayalam": (0x0D00, 0x0D7F),
    "Kannada": (0x0C80, 0x0CFF),
}


def detect_language(text: str) -> str:
    """
    Detects the primary language of the input text using Unicode code points.
    Returns: 'Tamil', 'Hindi', 'Telugu', 'Malayalam', 'Kannada', 'English', or 'Other'
    """
    if not text or not text.strip():
        return "English"

    clean_text = text.strip()

    # Count script characters
    counts: Dict[str, int] = {lang: 0 for lang in SCRIPT_RANGES}
    latin_count = 0

    for char in clean_text:
        cp = ord(char)
        matched = False
        for lang, (start, end) in SCRIPT_RANGES.items():
            if start <= cp <= end:
                counts[lang] += 1
                matched = True
                break
        if not matched and (('A' <= char <= 'Z') or ('a' <= char <= 'z')):
            latin_count += 1

    # Find language with highest count
    highest_lang = max(counts, key=counts.get)
    highest_count = counts[highest_lang]

    if highest_count > 0:
        return highest_lang

    if latin_count > 0:
        return "English"

    return "Other"
