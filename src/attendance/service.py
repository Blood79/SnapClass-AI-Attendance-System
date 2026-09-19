from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Iterable

@dataclass(frozen=True)
class AttendanceRecord:
    student_id: str
    subject_id: str
    status: str = "present"
    method: str = "manual"
    confidence: float | None = None
    timestamp: str | None = None
    def normalized(self) -> dict:
        data = asdict(self)
        data["timestamp"] = self.timestamp or datetime.now(timezone.utc).isoformat()
        if data["status"] not in {"present", "absent", "late"}:
            raise ValueError("Unsupported attendance status.")
        return data

def should_mark_present(confidence: float | None, threshold: float = 0.75) -> bool:
    return confidence is not None and 0 <= confidence <= 1 and confidence >= threshold

def deduplicate(records: Iterable[dict], student_id: str, subject_id: str, day: str) -> bool:
    return any(r.get("student_id") == student_id and r.get("subject_id") == subject_id and str(r.get("timestamp", "")).startswith(day) and r.get("status") == "present" for r in records)

def attendance_rate(records: Iterable[dict]) -> float:
    rows = list(records)
    if not rows: return 0.0
    present = sum(r.get("status") == "present" for r in rows)
    return round(100 * present / len(rows), 2)
