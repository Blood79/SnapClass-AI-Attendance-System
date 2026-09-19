from src.attendance.service import attendance_rate, deduplicate, should_mark_present

def test_threshold_logic():
    assert should_mark_present(0.80, 0.75); assert not should_mark_present(0.70, 0.75); assert not should_mark_present(None, 0.75)

def test_daily_duplicate_detection():
    rows = [{"student_id":"s1","subject_id":"sub1","status":"present","timestamp":"2026-09-19T09:00:00+00:00"}]
    assert deduplicate(rows, "s1", "sub1", "2026-09-19"); assert not deduplicate(rows, "s2", "sub1", "2026-09-19")

def test_attendance_rate(): assert attendance_rate([{"status":"present"},{"status":"absent"},{"status":"present"}]) == 66.67
