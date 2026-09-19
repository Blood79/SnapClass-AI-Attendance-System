from __future__ import annotations
from datetime import datetime, timezone
import streamlit as st
from src.attendance.service import AttendanceRecord, attendance_rate, deduplicate
from src.authentication.auth import Role, hash_password, verify_password
from src.config import settings
from src.database.repository import JsonRepository
from src.qr.service import issue_token

st.set_page_config(page_title="SnapClass", page_icon="📚", layout="wide")
repo = JsonRepository(settings.data_file)

def seed_demo() -> None:
    if repo.all("users"): return
    repo.add_user("teacher@snapclass.local", "Demo Teacher", Role.TEACHER.value, hash_password("teacher123"))
    repo.add_user("student@snapclass.local", "Demo Student", Role.STUDENT.value, hash_password("student123"))
seed_demo()

def login() -> dict | None:
    st.sidebar.title("SnapClass"); st.sidebar.caption("AI-assisted attendance platform")
    email = st.sidebar.text_input("Email", placeholder="you@example.com"); password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Sign in", use_container_width=True):
        user = repo.find_user(email)
        if user and verify_password(password, user["password_hash"]): st.session_state.user = user
        else: st.sidebar.error("Invalid credentials.")
    return st.session_state.get("user")

user = login()
if not user:
    st.title("SnapClass AI Attendance"); st.subheader("A portfolio-grade attendance workflow")
    c1, c2, c3 = st.columns(3); c1.metric("Biometric modes", "2"); c2.metric("Verification layer", "Face + Voice"); c3.metric("Default storage", "Local JSON")
    st.info("Demo accounts: teacher@snapclass.local / teacher123 and student@snapclass.local / student123")
    st.markdown("### Product flow\n1. Teacher creates a subject.\n2. Student joins through a signed QR payload.\n3. Attendance can be captured manually or through optional biometric adapters.\n4. Records remain separated from UI code for auditability and testing.")
    st.stop()

st.sidebar.success(f"Signed in as {user['name']} · {user['role']}")
if st.sidebar.button("Sign out", use_container_width=True): st.session_state.clear(); st.rerun()

if user["role"] == Role.TEACHER.value:
    st.title("Teacher Console"); tab1, tab2, tab3 = st.tabs(["Subjects", "QR Enrollment", "Attendance"])
    with tab1:
        st.subheader("Create a subject"); subject_name = st.text_input("Subject name")
        if st.button("Create subject") and subject_name.strip(): repo.add_subject(subject_name, user["id"]); st.success("Subject created.")
        rows = [s for s in repo.all("subjects") if s["teacher_id"] == user["id"]]; st.dataframe(rows, use_container_width=True, hide_index=True)
    with tab2:
        subjects = [s for s in repo.all("subjects") if s["teacher_id"] == user["id"]]
        if subjects:
            selected = st.selectbox("Subject", subjects, format_func=lambda x: x["name"])
            token = issue_token({"subject_id": selected["id"], "type": "enrollment"}, settings.qr_secret)
            st.code(token, language="text"); st.caption("Paste the signed token into the student join field. In deployment, render it as a QR code.")
        else: st.info("Create a subject first.")
    with tab3:
        rows = [r for r in repo.all("attendance") if r.get("teacher_id") == user["id"]]
        st.metric("Records", len(rows)); st.metric("Present rate", f"{attendance_rate(rows)}%"); st.dataframe(rows, use_container_width=True, hide_index=True)
else:
    st.title("Student Portal"); subjects = repo.all("subjects"); my_enrollments = {e["subject_id"] for e in repo.all("enrollments") if e["student_id"] == user["id"]}
    st.subheader("Join a class"); join_code = st.text_input("Signed QR token")
    if st.button("Join subject") and join_code:
        from src.qr.service import verify_token
        try:
            payload = verify_token(join_code, settings.qr_secret)
            if payload.get("type") != "enrollment": raise ValueError("Unexpected token type")
            repo.enroll(user["id"], payload["subject_id"]); st.success("Enrollment recorded."); st.rerun()
        except ValueError as exc: st.error(str(exc))
    joined = [s for s in subjects if s["id"] in my_enrollments]; st.subheader("My classes"); st.dataframe(joined, use_container_width=True, hide_index=True)
    if joined:
        subject = st.selectbox("Record demo attendance for", joined, format_func=lambda x: x["name"]); existing = repo.all("attendance"); today = datetime.now(timezone.utc).date().isoformat()
        if deduplicate(existing, user["id"], subject["id"], today): st.warning("Already marked present for this subject today.")
        elif st.button("Mark present (demo)"):
            record = AttendanceRecord(user["id"], subject["id"], method="demo").normalized(); record["teacher_id"] = subject["teacher_id"]; repo.add_attendance(record); st.success("Attendance recorded.")
    my_records = [r for r in repo.all("attendance") if r.get("student_id") == user["id"]]; st.metric("Attendance rate", f"{attendance_rate(my_records)}%"); st.dataframe(my_records, use_container_width=True, hide_index=True)
st.caption("Prototype notice: biometric verification requires the optional dependency set; production use requires consent, retention controls and anti-spoofing safeguards.")
