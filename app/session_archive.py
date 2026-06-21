from __future__ import annotations

import json
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Iterable

try:
    from app.utils import ensure_dir, load_config, write_json
except ImportError:
    from utils import ensure_dir, load_config, write_json


def _project_root_from_config(config_path: str) -> Path:
    return Path(config_path).resolve().parent.parent


def _unique_existing_paths(paths: Iterable[Path]) -> list[Path]:
    seen: set[str] = set()
    out: list[Path] = []
    for p in paths:
        rp = str(p.resolve())
        if p.exists() and rp not in seen:
            seen.add(rp)
            out.append(p)
    return out


def _collect_runtime_files(cfg: dict, project_root: Path) -> list[Path]:
    paths_cfg = cfg.get("paths", {})
    avatar_cfg = cfg.get("avatar", {})

    answers_dir = project_root / paths_cfg.get("answers_dir", "data/answers")
    chat_log_json = project_root / paths_cfg.get("chat_log_json", "data/answers/chat_log.json")
    lam_input_text = project_root / paths_cfg.get("lam_input_text", "data/answers/latest_answer.txt")
    lam_input_audio = project_root / paths_cfg.get("lam_input_audio", "data/answers/latest_answer.wav")
    lam_output_video = project_root / paths_cfg.get("lam_output_video", "data/answers/latest_avatar.mp4")
    avatar_input_text = project_root / paths_cfg.get("avatar_input_text", "data/answers/latest_avatar_script.txt")
    avatar_input_audio = project_root / paths_cfg.get("avatar_input_audio", "data/answers/latest_avatar.wav")

    avatar_result_dir = project_root / avatar_cfg.get("result_dir", "data/lam_work/sadtalker_results")
    lam_work_dir = project_root / paths_cfg.get("lam_work_dir", "data/lam_work")

    collected: list[Path] = [
        chat_log_json,
        lam_input_text,
        lam_input_audio,
        lam_output_video,
        avatar_input_text,
        avatar_input_audio,
    ]

    if answers_dir.exists():
        for pattern in ("*.txt", "*.json", "*.wav", "*.mp4"):
            collected.extend(sorted(answers_dir.glob(pattern)))

    if avatar_result_dir.exists():
        collected.extend(sorted(avatar_result_dir.rglob("*.mp4")))

    if lam_work_dir.exists():
        for pattern in ("*.txt", "*.json", "*.wav", "*.mp4"):
            collected.extend(sorted(lam_work_dir.rglob(pattern)))

    return _unique_existing_paths(collected)


def _write_manifest(
    archive_zip_path: Path,
    archived_files: list[Path],
    project_root: Path,
    timestamp: str,
) -> None:
    manifest = {
        "archived_at": timestamp,
        "archive_file": str(archive_zip_path),
        "files": [str(p.resolve().relative_to(project_root)) for p in archived_files],
    }

    with zipfile.ZipFile(archive_zip_path, mode="a", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.json", json.dumps(manifest, indent=2))


def _zip_files(archive_zip_path: Path, files_to_archive: list[Path], project_root: Path) -> None:
    with zipfile.ZipFile(archive_zip_path, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file_path in files_to_archive:
            try:
                arcname = str(file_path.resolve().relative_to(project_root))
            except Exception:
                arcname = file_path.name
            zf.write(file_path, arcname=arcname)


def _clear_directory_contents(dir_path: Path) -> None:
    if not dir_path.exists():
        return
    for child in dir_path.iterdir():
        if child.is_file() or child.is_symlink():
            child.unlink(missing_ok=True)
        elif child.is_dir():
            shutil.rmtree(child, ignore_errors=True)


def reset_runtime_files(config_path: str = "app/config.yaml") -> tuple[bool, str]:
    cfg = load_config(config_path)
    project_root = _project_root_from_config(config_path)
    paths_cfg = cfg.get("paths", {})
    avatar_cfg = cfg.get("avatar", {})

    answers_dir = project_root / paths_cfg.get("answers_dir", "data/answers")
    chat_log_json = project_root / paths_cfg.get("chat_log_json", "data/answers/chat_log.json")
    lam_work_dir = project_root / paths_cfg.get("lam_work_dir", "data/lam_work")
    avatar_result_dir = project_root / avatar_cfg.get("result_dir", "data/lam_work/sadtalker_results")

    ensure_dir(answers_dir)
    ensure_dir(lam_work_dir)

    _clear_directory_contents(answers_dir)

    # Recreate clean chat log so next startup has a valid empty file.
    write_json(str(chat_log_json), [])

    # Clean generated SadTalker working outputs too.
    if avatar_result_dir.exists():
        _clear_directory_contents(avatar_result_dir)

    return True, "Runtime files reset successfully."


def archive_and_reset_session(config_path: str = "app/config.yaml") -> tuple[bool, str, str]:
    cfg = load_config(config_path)
    project_root = _project_root_from_config(config_path)

    archive_dir = project_root / cfg.get("paths", {}).get("archive_dir", "data/archive")
    ensure_dir(archive_dir)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_zip_path = archive_dir / f"session_{timestamp}.zip"

    files_to_archive = _collect_runtime_files(cfg, project_root)

    try:
        if files_to_archive:
            _zip_files(archive_zip_path, files_to_archive, project_root)
            _write_manifest(archive_zip_path, files_to_archive, project_root, timestamp)
        else:
            with zipfile.ZipFile(archive_zip_path, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
                zf.writestr(
                    "manifest.json",
                    json.dumps(
                        {
                            "archived_at": timestamp,
                            "archive_file": str(archive_zip_path),
                            "files": [],
                            "note": "No runtime files were present to archive.",
                        },
                        indent=2,
                    ),
                )
    except Exception as e:
        return False, f"Failed to archive session: {e}", ""

    ok, reset_msg = reset_runtime_files(config_path=config_path)
    if not ok:
        return False, reset_msg, ""

    return True, f"Session archived and reset successfully.", str(archive_zip_path)