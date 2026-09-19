from __future__ import annotations
import json
from pathlib import Path
from threading import Lock
from uuid import uuid4

class JsonRepository:
    """Small deterministic repository for demos and local development."""
    def __init__(self, path: str = "data/demo.json") -> None:
        self.path = Path(path)
        self.lock = Lock()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists(): self._write(self._empty())
    @staticmethod
    def _empty() -> dict:
        return {"users": [], "subjects": [], "enrollments": [], "attendance": []}
    def _read(self) -> dict:
        try: return json.loads(self.path.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError): return self._empty()
    def _write(self, data: dict) -> None:
        self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    def all(self, collection: str) -> list[dict]: return list(self._read().get(collection, []))
    def find_user(self, email: str) -> dict | None:
        normalized = email.strip().lower()
        return next((u for u in self.all("users") if u.get("email") == normalized), None)
    def add_user(self, email: str, name: str, role: str, password_hash: str) -> dict:
        with self.lock:
            data = self._read(); normalized = email.strip().lower()
            if any(u.get("email") == normalized for u in data["users"]): raise ValueError("Account already exists.")
            user = {"id": str(uuid4()), "email": normalized, "name": name.strip(), "role": role, "password_hash": password_hash}
            data["users"].append(user); self._write(data); return user
    def add_subject(self, name: str, teacher_id: str) -> dict:
        with self.lock:
            data = self._read(); subject = {"id": str(uuid4()), "name": name.strip(), "teacher_id": teacher_id}
            data["subjects"].append(subject); self._write(data); return subject
    def enroll(self, student_id: str, subject_id: str) -> None:
        with self.lock:
            data = self._read(); row = {"student_id": student_id, "subject_id": subject_id}
            if row not in data["enrollments"]: data["enrollments"].append(row); self._write(data)
    def add_attendance(self, record: dict) -> dict:
        with self.lock:
            data = self._read(); data["attendance"].append(record); self._write(data); return record
