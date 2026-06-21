from __future__ import annotations

import os
from typing import Dict

import torch


def has_cuda() -> bool:
    return torch.cuda.is_available() and torch.cuda.device_count() > 0


def get_best_device() -> str:
    return "cuda" if has_cuda() else "cpu"


def get_torch_dtype():
    return torch.float16 if has_cuda() else torch.float32


def get_device_info() -> Dict[str, str]:
    if has_cuda():
        idx = torch.cuda.current_device()
        props = torch.cuda.get_device_properties(idx)
        return {
            "device": "cuda",
            "name": torch.cuda.get_device_name(idx),
            "total_vram_gb": f"{props.total_memory / (1024 ** 3):.2f}",
            "capability": f"{props.major}.{props.minor}",
        }
    return {
        "device": "cpu",
        "name": "CPU",
        "total_vram_gb": "0.00",
        "capability": "n/a",
    }


def configure_torch() -> None:
    try:
        torch.set_float32_matmul_precision("high")
    except Exception:
        pass

    if has_cuda():
        try:
            torch.backends.cuda.matmul.allow_tf32 = True
        except Exception:
            pass
        try:
            torch.backends.cudnn.allow_tf32 = True
        except Exception:
            pass
        try:
            torch.backends.cudnn.benchmark = True
        except Exception:
            pass

        os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")