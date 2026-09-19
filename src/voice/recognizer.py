from __future__ import annotations
import io
import numpy as np

class VoiceBackendUnavailable(RuntimeError): pass

class VoiceRecognizer:
    """MFCC + delta fingerprint adapter with cosine verification."""
    def __init__(self, threshold: float = 0.75) -> None:
        self.threshold = threshold; self._known: dict[str, np.ndarray] = {}
    def encode(self, audio_bytes: bytes) -> np.ndarray:
        try: import librosa
        except ImportError as exc: raise VoiceBackendUnavailable("Install requirements-biometric.txt for voice verification.") from exc
        y, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000, mono=True)
        if len(y) < sr // 2: raise ValueError("Audio sample is too short; record at least 0.5 seconds.")
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20); delta = librosa.feature.delta(mfcc)
        vector = np.concatenate([mfcc.mean(axis=1), mfcc.std(axis=1), delta.mean(axis=1), delta.std(axis=1)])
        norm = np.linalg.norm(vector); return vector / norm if norm else vector
    def register(self, student_id: str, audio_bytes: bytes) -> np.ndarray:
        vector = self.encode(audio_bytes); self._known[student_id] = vector; return vector
    def match(self, audio_bytes: bytes) -> tuple[str, float, bool]:
        if not self._known: raise ValueError("No registered voice fingerprints.")
        query = self.encode(audio_bytes); best_id, best_score = "", -1.0
        for student_id, vector in self._known.items():
            score = float(np.dot(query, vector))
            if score > best_score: best_id, best_score = student_id, score
        return best_id, best_score, best_score >= self.threshold
