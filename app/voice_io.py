from __future__ import annotations

from pathlib import Path
from typing import Optional
import json
import wave

try:
    from app.utils import ensure_dir, load_config
except ImportError:
    from utils import ensure_dir, load_config

from piper import PiperVoice
from vosk import Model, KaldiRecognizer
import sounddevice as sd
import soundfile as sf


class LocalTTS:
    def __init__(self, config_path: str = "app/config.yaml") -> None:
        self.cfg = load_config(config_path)
        self.voice_cfg = self.cfg.get("voice", {})
        self.enabled = bool(self.voice_cfg.get("enable_piper", False))
        self.model_path = Path(self.voice_cfg.get("piper_model_path", ""))
        self.config_path = Path(self.voice_cfg.get("piper_config_path", ""))
        self._voice: Optional[PiperVoice] = None

    def is_ready(self) -> bool:
        return self.enabled and self.model_path.exists() and self.config_path.exists()

    def load(self) -> PiperVoice:
        if not self.is_ready():
            raise FileNotFoundError(
                f"Piper model/config not found or disabled. "
                f"model={self.model_path} config={self.config_path} enabled={self.enabled}"
            )

        if self._voice is None:
            self._voice = PiperVoice.load(
                model_path=str(self.model_path),
                config_path=str(self.config_path),
            )

        return self._voice

    def synthesize_to_wav(self, text: str, wav_path: str | Path) -> str:
        wav_path = Path(wav_path)
        ensure_dir(wav_path.parent)

        cleaned = (text or "").strip()
        if not cleaned:
            raise ValueError("Cannot synthesize empty text.")

        voice = self.load()

        with wave.open(str(wav_path), "wb") as wav_file:
            voice.synthesize_wav(cleaned, wav_file)

        return str(wav_path)


class LocalSTT:
    def __init__(self, config_path: str = "app/config.yaml") -> None:
        self.cfg = load_config(config_path)
        self.voice_cfg = self.cfg.get("voice", {})
        self.enabled = bool(self.voice_cfg.get("enable_vosk", False))
        self.model_dir = Path(self.voice_cfg.get("vosk_model_dir", ""))
        self.sample_rate = 16000
        self.channels = 1
        self.dtype = "int16"
        self.input_device = self.voice_cfg.get("input_device", None)
        self._model: Optional[Model] = None

    def is_ready(self) -> bool:
        return self.enabled and self.model_dir.exists()

    def load(self) -> Model:
        if not self.is_ready():
            raise FileNotFoundError(
                f"Vosk model not found or disabled. model_dir={self.model_dir} enabled={self.enabled}"
            )

        if self._model is None:
            try:
                self._model = Model(str(self.model_dir))
            except Exception as e:
                raise RuntimeError(
                    f"Failed to create Vosk model from '{self.model_dir}'. "
                    f"Check that this folder directly contains model files like am, conf, graph, ivector. "
                    f"Original error: {e}"
                ) from e

        return self._model

    def list_input_devices(self) -> list[dict]:
        devices = sd.query_devices()
        results = []
        for i, d in enumerate(devices):
            if d["max_input_channels"] > 0:
                results.append(
                    {
                        "index": i,
                        "name": d["name"],
                        "max_input_channels": d["max_input_channels"],
                        "default_samplerate": d["default_samplerate"],
                    }
                )
        return results

    def record_to_wav(self, wav_path: str | Path, duration_seconds: int = 5) -> str:
        wav_path = Path(wav_path)
        ensure_dir(wav_path.parent)

        audio = sd.rec(
            int(duration_seconds * self.sample_rate),
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype="float32",
            device=self.input_device,
        )
        sd.wait()

        peak = float(abs(audio).max()) if audio.size else 0.0
        if peak > 0:
            target_peak = 0.8
            gain = min(target_peak / peak, 20.0)
            audio = audio * gain
            audio = audio.clip(-1.0, 1.0)

        sf.write(str(wav_path), audio, self.sample_rate, subtype="PCM_16")
        return str(wav_path)

    def transcribe_wav(self, wav_path: str | Path) -> str:
        wav_path = Path(wav_path)
        if not wav_path.exists():
            raise FileNotFoundError(f"Audio file not found: {wav_path}")

        model = self.load()
        recognizer = KaldiRecognizer(model, self.sample_rate)
        recognizer.SetWords(True)

        got_text_parts: list[str] = []

        with wave.open(str(wav_path), "rb") as wf:
            if wf.getnchannels() != 1:
                raise ValueError("Audio must be mono.")
            if wf.getsampwidth() != 2:
                raise ValueError("Audio must be 16-bit PCM.")
            if wf.getframerate() != self.sample_rate:
                raise ValueError(f"Audio must be {self.sample_rate} Hz.")

            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if recognizer.AcceptWaveform(data):
                    part = json.loads(recognizer.Result()).get("text", "").strip()
                    if part:
                        got_text_parts.append(part)

        final_result = json.loads(recognizer.FinalResult())
        final_text = (final_result.get("text") or "").strip()
        if final_text:
            got_text_parts.append(final_text)

        return " ".join(got_text_parts).strip()

    def record_and_transcribe(self, wav_path: str | Path, duration_seconds: int = 5) -> tuple[str, str]:
        saved_wav = self.record_to_wav(wav_path=wav_path, duration_seconds=duration_seconds)
        text = self.transcribe_wav(saved_wav)
        return saved_wav, text