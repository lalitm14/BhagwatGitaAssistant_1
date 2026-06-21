from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Dict, List, Optional

from pypdf import PdfReader

from utils import ensure_dir, load_config, write_json


def normalize_ws(text: str) -> str:
    return re.sub(r"[ \t]+", " ", (text or "")).strip()


def maybe_fix_mojibake(text: str) -> str:
    if not text:
        return text
    if "à¤" in text or "Ã" in text or "Â" in text:
        try:
            return text.encode("latin1", errors="ignore").decode("utf-8", errors="ignore")
        except Exception:
            return text
    return text


def clean_multiline_text(text: str) -> str:
    if text is None:
        return ""
    text = str(text)
    text = text.replace("\\n", "\n").replace("\\r", "\r")
    text = maybe_fix_mojibake(text)
    lines = [normalize_ws(line) for line in text.splitlines()]
    lines = [line for line in lines if line]
    return "\n".join(lines).strip()


def extract_pdf_pages(pdf_path: str) -> List[str]:
    reader = PdfReader(pdf_path)
    return [(page.extract_text() or "") for page in reader.pages]


def best_pdf_match(chapter: int, verse_num: int, pages: List[str]) -> Dict[str, Optional[str]]:
    target_text_label = f"TEXT {verse_num}"
    best_page = None
    best_text = ""
    best_score = -1

    for idx, raw in enumerate(pages, start=1):
        page = raw or ""
        score = 0

        if target_text_label in page:
            score += 5
        if re.search(rf"\b{verse_num}\b", page):
            score += 1
        if re.search(rf"\bCHAPTER\s+{chapter}\b", page, re.IGNORECASE):
            score += 2

        if score > best_score:
            best_score = score
            best_page = idx
            best_text = page

    excerpt = ""
    if best_text:
        lines = [normalize_ws(x) for x in best_text.splitlines() if normalize_ws(x)]
        excerpt = " ".join(lines[:30])

    return {
        "page": best_page,
        "english_pdf_excerpt": excerpt,
    }


def load_clean_csv(csv_path: str) -> List[Dict]:
    rows: List[Dict] = []
    with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            chapter = int(str(row.get("chapter", "")).strip())
            verse = str(row.get("verse", "")).strip()

            shlok = clean_multiline_text(row.get("shlok", ""))
            transliteration = clean_multiline_text(row.get("transliteration", ""))
            translation = clean_multiline_text(row.get("translation", ""))

            rows.append(
                {
                    "chapter": chapter,
                    "verse": verse,
                    "sanskrit": shlok,
                    "transliteration": transliteration,
                    "english_dataset": translation,
                }
            )
    return rows


def build_structured(clean_rows: List[Dict], pdf_pages: List[str]) -> List[Dict]:
    structured: List[Dict] = []

    for i, row in enumerate(clean_rows):
        verse = row["verse"]
        try:
            verse_num = int(str(verse).split(".")[1])
        except Exception:
            verse_num = 0

        pdf_match = best_pdf_match(row["chapter"], verse_num, pdf_pages)

        english_pdf_excerpt = clean_multiline_text(pdf_match.get("english_pdf_excerpt") or "")
        page = pdf_match.get("page")

        combined_parts = [
            f"Chapter {row['chapter']} Verse {verse}",
            row["sanskrit"],
            row["transliteration"],
            row["english_dataset"],
        ]

        if english_pdf_excerpt:
            combined_parts.append(f"PDF context: {english_pdf_excerpt}")

        combined_text = "\n\n".join([p for p in combined_parts if p])

        structured.append(
            {
                "record_id": f"gita_{i+1}",
                "chapter": row["chapter"],
                "verse": verse,
                "page": page,
                "sanskrit": row["sanskrit"],
                "transliteration": row["transliteration"],
                "english_dataset": row["english_dataset"],
                "english_pdf_excerpt": english_pdf_excerpt,
                "combined_text": combined_text,
                "source_file": "snskrt/Shrimad_Bhagavad_Gita + local PDF",
            }
        )

    return structured


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="app/config.yaml")
    parser.add_argument("--csv", default="data/gita_clean_source.csv")
    args = parser.parse_args()

    cfg = load_config(args.config)
    pdf_path = cfg["paths"]["pdf_path"]
    structured_json_path = cfg["paths"]["structured_json_path"]

    pdf_pages = extract_pdf_pages(pdf_path)
    clean_rows = load_clean_csv(args.csv)
    structured = build_structured(clean_rows, pdf_pages)

    ensure_dir(Path(structured_json_path).parent)
    write_json(Path(structured_json_path), structured)

    print(
        json.dumps(
            {
                "structured_json_path": structured_json_path,
                "num_records": len(structured),
                "sample_first_verse": structured[0]["verse"] if structured else None,
                "sample_first_sanskrit": structured[0]["sanskrit"][:120] if structured else None,
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()