from dataclasses import dataclass
import os

@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "SnapClass")
    data_file: str = os.getenv("SNAPCLASS_DATA_FILE", "data/demo.json")
    qr_secret: str = os.getenv("SNAPCLASS_QR_SECRET", "change-me-in-production")
    face_threshold: float = float(os.getenv("FACE_THRESHOLD", "0.60"))
    voice_threshold: float = float(os.getenv("VOICE_THRESHOLD", "0.75"))
    biometric_retention_days: int = int(os.getenv("BIOMETRIC_RETENTION_DAYS", "30"))

settings = Settings()
