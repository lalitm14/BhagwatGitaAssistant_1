from __future__ import annotations

import pickle
import sys
from pathlib import Path
from typing import Any, Sequence, Tuple

import numpy as np

try:
    import app.utils as utils_module
except ImportError:
    import utils as utils_module  # type: ignore

# Backward compatibility for older pickle files that stored objects as utils.Chunk
sys.modules.setdefault("utils", utils_module)

try:
    import faiss  # type: ignore

    FAISS_AVAILABLE = True
except Exception:
    faiss = None
    FAISS_AVAILABLE = False


class LocalVectorStore:
    def __init__(self, embeddings: np.ndarray, metadata: Sequence[Any], backend: str) -> None:
        self.embeddings = embeddings.astype("float32")
        self.metadata = list(metadata)
        self.backend = backend
        self.index = None

        if self.backend == "faiss":
            if not FAISS_AVAILABLE:
                raise RuntimeError("FAISS backend requested but faiss is not installed.")
            dim = self.embeddings.shape[1]
            index = faiss.IndexFlatIP(dim)
            faiss.normalize_L2(self.embeddings)
            index.add(self.embeddings)
            self.index = index
        else:
            self.embeddings = self._normalize(self.embeddings)

    @staticmethod
    def _normalize(x: np.ndarray) -> np.ndarray:
        norms = np.linalg.norm(x, axis=1, keepdims=True)
        norms = np.clip(norms, 1e-12, None)
        return x / norms

    def search(self, query_vectors: np.ndarray, top_k: int) -> Tuple[np.ndarray, np.ndarray]:
        q = query_vectors.astype("float32")

        if self.backend == "faiss":
            if self.index is None:
                raise RuntimeError("FAISS index is not loaded.")
            faiss.normalize_L2(q)
            scores, idxs = self.index.search(q, top_k)
            return scores, idxs

        q = self._normalize(q)
        sims = np.matmul(q, self.embeddings.T)
        idxs = np.argsort(-sims, axis=1)[:, :top_k]
        scores = np.take_along_axis(sims, idxs, axis=1)
        return scores, idxs

    def save(self, index_dir: str | Path) -> None:
        index_dir = Path(index_dir)
        index_dir.mkdir(parents=True, exist_ok=True)

        with open(index_dir / "metadata.pkl", "wb") as f:
            pickle.dump(self.metadata, f)

        with open(index_dir / "backend.txt", "w", encoding="utf-8") as f:
            f.write(self.backend)

        if self.backend == "faiss":
            if self.index is None:
                raise RuntimeError("Cannot save FAISS backend: index is not initialized.")
            faiss.write_index(self.index, str(index_dir / "gita.index"))
        else:
            np.save(index_dir / "embeddings.npy", self.embeddings)

    @classmethod
    def load(cls, index_dir: str | Path) -> "LocalVectorStore":
        index_dir = Path(index_dir)

        with open(index_dir / "metadata.pkl", "rb") as f:
            metadata = pickle.load(f)

        backend_file = index_dir / "backend.txt"
        backend = backend_file.read_text(encoding="utf-8").strip() if backend_file.exists() else "faiss"

        if backend == "faiss":
            if not FAISS_AVAILABLE:
                raise RuntimeError(
                    "This index was built with FAISS, but faiss is not installed in the current environment."
                )

            index_path = index_dir / "gita.index"
            if not index_path.exists():
                raise FileNotFoundError(f"FAISS index file not found: {index_path}")

            index = faiss.read_index(str(index_path))
            dim = int(index.d)

            dummy = np.zeros((1, dim), dtype="float32")
            store = cls(dummy, metadata, backend="faiss")
            store.index = index
            store.embeddings = None
            return store

        embeddings_path = index_dir / "embeddings.npy"
        if not embeddings_path.exists():
            raise FileNotFoundError(f"Embeddings file not found: {embeddings_path}")

        embeddings = np.load(embeddings_path)
        return cls(embeddings, metadata, backend="numpy")