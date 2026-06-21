from __future__ import annotations

import shutil
import subprocess
import time
from pathlib import Path
from typing import Tuple

try:
    from app.utils import ensure_dir, load_config
except ImportError:
    from utils import ensure_dir, load_config


class AvatarPipeline:
    def __init__(self, config_path: str = "app/config.yaml") -> None:
        self.cfg = load_config(config_path)
        self.paths = self.cfg.get("paths", {})
        self.avatar_cfg = self.cfg.get("avatar", {})

        self.enabled = bool(self.avatar_cfg.get("enable_avatar", False))
        self.engine = str(self.avatar_cfg.get("engine", "sadtalker")).lower()

        self.sadtalker_repo_dir = Path(
            self.avatar_cfg.get("sadtalker_repo_dir", "models/SadTalker")
        )
        self.sadtalker_python_exe = Path(
            self.avatar_cfg.get(
                "sadtalker_python_exe",
                r"C:\offline_gita_avatar\sadtalker_env\Scripts\python.exe",
            )
        )
        self.source_image = Path(self.avatar_cfg.get("source_image", "models/avatar/user.jpg"))
        self.result_dir = Path(self.avatar_cfg.get("result_dir", "data/lam_work/sadtalker_results"))
        self.output_video = Path(
            self.avatar_cfg.get("output_video", "data/answers/latest_avatar.mp4")
        )

        self.input_audio = Path(
            self.paths.get("lam_input_audio", "data/answers/latest_answer.wav")
        )
        self.input_text = Path(
            self.paths.get("lam_input_text", "data/answers/latest_answer.txt")
        )

        self.use_cpu = bool(self.avatar_cfg.get("use_cpu", True))
        self.preprocess = str(self.avatar_cfg.get("preprocess", "full"))
        self.still = bool(self.avatar_cfg.get("still", True))
        self.enhancer = str(self.avatar_cfg.get("enhancer", "none")).lower()

    def is_ready(self) -> Tuple[bool, str]:
        if not self.enabled:
            return False, "Avatar pipeline disabled in config."
        if self.engine != "sadtalker":
            return False, f"Unsupported avatar engine: {self.engine}"
        if not self.sadtalker_repo_dir.exists():
            return False, f"SadTalker repo not found: {self.sadtalker_repo_dir}"
        if not self.sadtalker_python_exe.exists():
            return False, f"SadTalker Python not found: {self.sadtalker_python_exe}"
        if not self.source_image.exists():
            return False, f"Source image not found: {self.source_image}"
        if not self.input_audio.exists():
            return False, f"Input audio not found: {self.input_audio}"
        return True, "SadTalker avatar pipeline ready."

    def _build_command(self) -> list[str]:
        cmd = [
            str(self.sadtalker_python_exe),
            "inference.py",
            "--driven_audio",
            str(self.input_audio.resolve()),
            "--source_image",
            str(self.source_image.resolve()),
            "--result_dir",
            str(self.result_dir.resolve()),
            "--preprocess",
            self.preprocess,
        ]

        if self.still:
            cmd.append("--still")

        if self.use_cpu:
            cmd.append("--cpu")

        if self.enhancer and self.enhancer != "none":
            cmd.extend(["--enhancer", self.enhancer])

        return cmd

    def _find_latest_mp4(self, newer_than: float | None = None) -> Path | None:
        if not self.result_dir.exists():
            return None

        mp4s = []
        for p in self.result_dir.rglob("*.mp4"):
            try:
                mtime = p.stat().st_mtime
            except OSError:
                continue
            if newer_than is None or mtime >= newer_than:
                mp4s.append((mtime, p))

        mp4s.sort(key=lambda x: x[0], reverse=True)
        return mp4s[0][1] if mp4s else None

    def run(self) -> Tuple[bool, str]:
        ready, msg = self.is_ready()
        if not ready:
            return False, msg

        ensure_dir(self.result_dir)
        ensure_dir(self.output_video.parent)

        start_time = time.time() - 1.0

        if self.output_video.exists():
            try:
                self.output_video.unlink()
            except OSError:
                pass

        cmd = self._build_command()

        try:

            proc = subprocess.run(
                cmd,
                cwd=str(self.sadtalker_repo_dir),
                capture_output=True,
                text=True,
                check=False,
            )
        except Exception as e:
            return False, f"Failed to start SadTalker: {e}"

        if proc.returncode != 0:
            return False, (
                "SadTalker failed.\n\n"
                f"Command: {' '.join(cmd)}\n\n"
                f"STDOUT:\n{proc.stdout}\n\n"
                f"STDERR:\n{proc.stderr}"
            )

        latest_mp4 = self._find_latest_mp4(newer_than=start_time)
        if latest_mp4 is None:
            latest_mp4 = self._find_latest_mp4()

        if latest_mp4 is None:
            return False, (
                "SadTalker finished but no MP4 was found.\n\n"
                f"STDOUT:\n{proc.stdout}\n\n"
                f"STDERR:\n{proc.stderr}"
            )

        try:
            shutil.copy2(latest_mp4, self.output_video)
        except Exception as e:
            return False, (
                f"SadTalker created an MP4 at {latest_mp4}, but copying to {self.output_video} failed: {e}\n\n"
                f"STDOUT:\n{proc.stdout}\n\n"
                f"STDERR:\n{proc.stderr}"
            )

        if not self.output_video.exists():
            return False, f"Expected output video was not found after copy: {self.output_video}"

        return True, str(self.output_video)
