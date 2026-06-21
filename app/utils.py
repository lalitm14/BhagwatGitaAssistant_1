from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Iterable, List

import yaml


@dataclass
class Chunk:
    chunk_id: str
    source_file: str
    page: int
    chapter: str | None
    verse: str | None
    sanskrit: str
    english: str
    combined_text: str


def load_config(config_path: str | os.PathLike) -> Dict[str, Any]:
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def ensure_dir(path: str | os.PathLike) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def write_json(path: str | os.PathLike, data: Any) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def read_json(path: str | os.PathLike, default: Any = None) -> Any:
    p = Path(path)
    if not p.exists():
        return default
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def save_chunks_jsonl(path: str | os.PathLike, chunks: Iterable[Chunk]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for chunk in chunks:
            f.write(json.dumps(asdict(chunk), ensure_ascii=False) + "\n")


def load_chunks_jsonl(path: str | os.PathLike) -> List[Chunk]:
    items: List[Chunk] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                items.append(Chunk(**json.loads(line)))
    return items


def normalize_ws(text: str) -> str:
    return " ".join(text.replace("\u00a0", " ").split())
