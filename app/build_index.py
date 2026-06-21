from __future__ import annotations

import argparse
import json
from pathlib import Path

from sentence_transformers import SentenceTransformer

from gpu_utils import configure_torch, get_best_device, get_device_info
from utils import Chunk, ensure_dir, load_config
from vector_store import LocalVectorStore


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="app/config.yaml")
    args = parser.parse_args()

    cfg = load_config(args.config)
    configure_torch()

    structured_json_path = Path(cfg["paths"]["structured_json_path"])
    index_dir = Path(cfg["paths"]["index_dir"])
    chunks_jsonl = Path(cfg["paths"]["chunks_jsonl"])

    data = json.loads(structured_json_path.read_text(encoding="utf-8"))

    chunks = []
    texts = []

    for row in data:
        english_dataset = (row.get("english_dataset") or "").strip()
        english_pdf_excerpt = (row.get("english_pdf_excerpt") or "").strip()
        sanskrit = (row.get("sanskrit") or "").strip()
        transliteration = (row.get("transliteration") or "").strip()

        english_primary = english_dataset

        combined_parts = [
            f"Chapter {row.get('chapter')} Verse {row.get('verse')}",
            sanskrit,
            transliteration,
            english_dataset,
        ]

        if english_pdf_excerpt:
            combined_parts.append(f"PDF context: {english_pdf_excerpt}")

        combined = "\n\n".join([p for p in combined_parts if p]).strip()

        chunk = Chunk(
            chunk_id=row["record_id"],
            page=row.get("page"),
            chapter=row.get("chapter"),
            verse=row.get("verse"),
            sanskrit=sanskrit,
            english=english_primary,
            combined_text=combined,
            source_file=row.get("source_file", "gita_clean_source"),
        )
        chunks.append(chunk)
        texts.append(combined)

    device = get_best_device() if cfg.get("performance", {}).get("prefer_gpu", True) else "cpu"
    embedder = SentenceTransformer(
        cfg["models"]["embedding_model"],
        device=device,
    )

    embeddings = embedder.encode(
        texts,
        batch_size=int(cfg.get("performance", {}).get("embedding_batch_size", 32)),
        convert_to_numpy=True,
        normalize_embeddings=False,
        show_progress_bar=True,
    ).astype("float32")

    store = LocalVectorStore(
        embeddings=embeddings,
        metadata=chunks,
        backend="faiss" if cfg["retrieval"].get("use_faiss", True) else "numpy",
    )

    ensure_dir(index_dir)
    store.save(index_dir)

    ensure_dir(chunks_jsonl.parent)
    with open(chunks_jsonl, "w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c.__dict__, ensure_ascii=False) + "\n")

    print(
        json.dumps(
            {
                "structured_json_path": str(structured_json_path),
                "num_chunks": len(chunks),
                "embedding_model": cfg["models"]["embedding_model"],
                "index_dir": str(index_dir),
                "device_used_for_embeddings": device,
                "device_info": get_device_info(),
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()