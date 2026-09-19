from __future__ import annotations
from dataclasses import dataclass
import numpy as np

class FaceBackendUnavailable(RuntimeError): pass

@dataclass
class FaceMatch:
    student_id: str
    distance: float
    accepted: bool

class FaceVerifier:
    """Optional face_recognition adapter with configurable distance threshold."""
    def __init__(self, threshold: float = 0.60) -> None:
        self.threshold = threshold; self._known: dict[str, np.ndarray] = {}
    @staticmethod
    def _backend():
        try:
            import face_recognition
            return face_recognition
        except ImportError as exc:
            raise FaceBackendUnavailable("Install requirements-biometric.txt for face verification.") from exc
    def encode_image(self, image) -> np.ndarray:
        backend = self._backend(); encodings = backend.face_encodings(np.asarray(image))
        if not encodings: raise ValueError("No detectable face found.")
        if len(encodings) > 1: raise ValueError("Use an image containing one face.")
        vector = np.asarray(encodings[0], dtype=float)
        if vector.shape != (128,): raise ValueError("Unexpected face descriptor shape.")
        return vector
    def register(self, student_id: str, image) -> np.ndarray:
        vector = self.encode_image(image); self._known[student_id] = vector; return vector
    def match(self, image) -> FaceMatch:
        if not self._known: raise ValueError("No registered face embeddings.")
        query = self.encode_image(image); ids = list(self._known)
        matrix = np.vstack([self._known[sid] for sid in ids]); distances = np.linalg.norm(matrix - query, axis=1)
        idx = int(np.argmin(distances)); distance = float(distances[idx])
        return FaceMatch(ids[idx], distance, distance <= self.threshold)
