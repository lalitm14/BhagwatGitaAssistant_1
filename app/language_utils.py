from __future__ import annotations

import re
from typing import Iterable, List

DEVANAGARI_RE = re.compile(r"[\u0900-\u097F]")
BENGALI_RE = re.compile(r"[\u0980-\u09FF]")
GURMUKHI_RE = re.compile(r"[\u0A00-\u0A7F]")
GUJARATI_RE = re.compile(r"[\u0A80-\u0AFF]")
ORIYA_RE = re.compile(r"[\u0B00-\u0B7F]")
TAMIL_RE = re.compile(r"[\u0B80-\u0BFF]")
TELUGU_RE = re.compile(r"[\u0C00-\u0C7F]")
KANNADA_RE = re.compile(r"[\u0C80-\u0CFF]")
MALAYALAM_RE = re.compile(r"[\u0D00-\u0D7F]")
LATIN_RE = re.compile(r"[A-Za-z]")

SCRIPT_RULES = [
    ("Sanskrit", DEVANAGARI_RE),
    ("Hindi", DEVANAGARI_RE),
    ("Marathi", DEVANAGARI_RE),
    ("Nepali", DEVANAGARI_RE),
    ("Bengali", BENGALI_RE),
    ("Punjabi", GURMUKHI_RE),
    ("Gujarati", GUJARATI_RE),
    ("Odia", ORIYA_RE),
    ("Tamil", TAMIL_RE),
    ("Telugu", TELUGU_RE),
    ("Kannada", KANNADA_RE),
    ("Malayalam", MALAYALAM_RE),
    ("English", LATIN_RE),
]


def detect_document_language(samples: Iterable[str]) -> str:
    text = " ".join(s for s in samples if s).strip()
    if not text:
        return "Unknown"

    scores = {}
    for lang, pattern in SCRIPT_RULES:
        matches = pattern.findall(text)
        if matches:
            scores[lang] = len(matches)

    if not scores:
        return "Unknown"

    devanagari_score = max(
        scores.get("Sanskrit", 0),
        scores.get("Hindi", 0),
        scores.get("Marathi", 0),
        scores.get("Nepali", 0),
    )
    english_score = scores.get("English", 0)

    if devanagari_score > 20 and english_score > 20:
        return "Bilingual (Indic + English)"

    best_lang = max(scores.items(), key=lambda kv: kv[1])[0]
    return best_lang


def get_supported_document_languages() -> List[str]:
    return [
        "Auto",
        "Bilingual (Indic + English)",
        "English",
        "Sanskrit",
        "Hindi",
        "Marathi",
        "Bengali",
        "Gujarati",
        "Punjabi",
        "Odia",
        "Tamil",
        "Telugu",
        "Kannada",
        "Malayalam",
        "Other",
    ]


def get_supported_answer_languages() -> List[str]:
    return ["English", "Hindi", "Sanskrit"]


def get_supported_query_languages() -> List[str]:
    return ["Auto", "English", "Sanskrit", "Same as document"]
