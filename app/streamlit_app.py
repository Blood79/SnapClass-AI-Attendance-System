from __future__ import annotations
from datetime import datetime, timezone
from io import BytesIO

import streamlit as st
from PIL import Image

from src.attendance.service import AttendanceRecord, attendance_rate, deduplicate
from src.authentication.auth import Role, hash_password, verify_password
from src.computer_vision.face import FaceBackendUnavailable, FaceVerifier
from src.config import settings
from src.database.repository import JsonRepository
from src.qr.render import render_qr
from src.qr.service import issue_token
from src.voice.recognizer import VoiceBackendUnavailable, VoiceRecognizer

st.set_page_config(page_title="SnapClass", page_icon="📚", layout="wide")
repo = JsonRepository(settings.data_file)


def seed_demo() -> None:
    if repo.all("users"):
        return
    repo.add_user("teacher@snapclass.local", "Demo Teacher", Role.TEACHER.value, hash_password("teacher123"))
    repo.add_user("student@snapclass.local", "Demo Student", Role.STUDENT.value, hash_password("student123"))


seed_demo()


def login() -> dict | None:
    st.sidebar.title("SnapClass")
    st.sidebar.caption("AI-assisted attendance platform")
    email = st.sidebar.text_input("Email", placeholder="you@example.com")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Sign in", use_container_width=True):
        user = repo.find_user(email)
        if user and verify_password(password, user["password_hash"]):
            st.session_state.user = user
        else:
            st.sidebar.error("Invalid credentials.")
    return st.session_state.get("user")


user = login()
if not user:
    st.title("SnapClass AI Attendance")
    st.subheader("A portfolio-grade attendance workflow")
    c1, c2, c3 = st.columns(3)
    c1.metric("Biometric modes", "2")
    c2.metric("QR security", "Signed + expiring")
    c3.metric("Default storage", "Local JSON")
    st.info("Demo accounts: teacher@snapclass.local / teacher123 and student@snapclass.local / student123")
    st.markdown(
        "### Product flow\n"
        "1. Teacher creates a subject.\n"
        "2. Student joins through a signed QR payload.\n"
        "3. Attendance can be captured through demo rules or optional biometric adapters.\n"
        "4. Records remain separated from UI code for auditability and testing."
    )
    st.stop()

st.sidebar.success(f"Signed in as {user['name']} · {user['role']}")
if st.sidebar.button("Sign out", use_container_width=True):
    st.session_state.clear()
    st.rerun()

common_tab, biometric_tab = st.tabs(["Dashboard", "Biometric Lab"])

with common_tab:
    if user["role"] == Role.TEACHER.value:
        st.title("Teacher Console")
        tab1, tab2, tab3 = st.tabs(["Subjects", "QR Enrollment", "Attendance"])
        with tab1:
            st.subheader("Create a subject")
            subject_name = st.text_input("Subject name")
            if st.button("Create subject") and subject_name.strip():
                repo.add_subject(subject_name, user["id"])
                st.success("Subject created.")
            rows = [s for s in repo.all("subjects") if s["teacher_id"] == user["id"]]
            st.dataframe(rows, use_container_width=True, hide_index=True)
        with tab2:
            subjects = [s for s in repo.all("subjects") if s["teacher_id"] == user["id"]]
            if subjects:
                selected = st.selectbox("Subject", subjects, format_func=lambda x: x["name"])
                token = issue_token({"subject_id": selected["id"], "type": "enrollment"}, settings.qr_secret)
                qr_bytes = render_qr(token)
                c1, c2 = st.columns([1, 2])
                with c1:
                    st.image(qr_bytes, caption="Enrollment QR", width=220)
                with c2:
                    st.code(token, language="text")
                    st.download_button("Download QR", qr_bytes, file_name="snapclass-enrollment.png", mime="image/png")
                    st.caption("The token is signed and expires automatically. Keep production signing secrets outside Git.")
            else:
                st.info("Create a subject first.")
        with tab3:
            rows = [r for r in repo.all("attendance") if r.get("teacher_id") == user["id"]]
            st.metric("Records", len(rows))
            st.metric("Present rate", f"{attendance_rate(rows)}%")
            st.dataframe(rows, use_container_width=True, hide_index=True)
    else:
        st.title("Student Portal")
        subjects = repo.all("subjects")
        my_enrollments = {e["subject_id"] for e in repo.all("enrollments") if e["student_id"] == user["id"]}
        st.subheader("Join a class")
        join_code = st.text_input("Signed QR token")
        if st.button("Join subject") and join_code:
            from src.qr.service import verify_token
            try:
                payload = verify_token(join_code, settings.qr_secret)
                if payload.get("type") != "enrollment":
                    raise ValueError("Unexpected token type")
                if not any(s["id"] == payload["subject_id"] for s in subjects):
                    raise ValueError("Subject does not exist in this repository.")
                repo.enroll(user["id"], payload["subject_id"])
                st.success("Enrollment recorded.")
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))
        joined = [s for s in subjects if s["id"] in my_enrollments]
        st.subheader("My classes")
        st.dataframe(joined, use_container_width=True, hide_index=True)
        if joined:
            subject = st.selectbox("Record demo attendance for", joined, format_func=lambda x: x["name"])
            existing = repo.all("attendance")
            today = datetime.now(timezone.utc).date().isoformat()
            if deduplicate(existing, user["id"], subject["id"], today):
                st.warning("Already marked present for this subject today.")
            elif st.button("Mark present (demo)"):
                record = AttendanceRecord(user["id"], subject["id"], method="demo").normalized()
                record["teacher_id"] = subject["teacher_id"]
                repo.add_attendance(record)
                st.success("Attendance recorded.")
        my_records = [r for r in repo.all("attendance") if r.get("student_id") == user["id"]]
        st.metric("Attendance rate", f"{attendance_rate(my_records)}%")
        st.dataframe(my_records, use_container_width=True, hide_index=True)

with biometric_tab:
    st.subheader("Biometric Lab")
    st.caption("This sandbox exercises the biometric adapters without persisting raw media or biometric vectors.")
    ftab, vtab = st.tabs(["Face verification", "Voice verification"])

    with ftab:
        c1, c2 = st.columns(2)
        with c1:
            ref = st.file_uploader("Reference face", type=["jpg", "jpeg", "png"], key="face_ref")
        with c2:
            probe = st.file_uploader("Probe face", type=["jpg", "jpeg", "png"], key="face_probe")
        if st.button("Run face verification", disabled=not (ref and probe)):
            try:
                verifier = FaceVerifier(settings.face_threshold)
                verifier.register("demo-student", Image.open(BytesIO(ref.getvalue())))
                result = verifier.match(Image.open(BytesIO(probe.getvalue())))
                st.metric("Distance", f"{result.distance:.4f}")
                st.success("Accepted match." if result.accepted else "Rejected match.")
            except (FaceBackendUnavailable, ValueError) as exc:
                st.error(str(exc))

    with vtab:
        c1, c2 = st.columns(2)
        with c1:
            vref = st.file_uploader("Reference audio", type=["wav", "mp3", "m4a", "ogg"], key="voice_ref")
        with c2:
            vprobe = st.file_uploader("Probe audio", type=["wav", "mp3", "m4a", "ogg"], key="voice_probe")
        if st.button("Run voice verification", disabled=not (vref and vprobe)):
            try:
                recognizer = VoiceRecognizer(settings.voice_threshold)
                recognizer.register("demo-student", vref.getvalue())
                student_id, score, accepted = recognizer.match(vprobe.getvalue())
                st.metric("Cosine similarity", f"{score:.4f}")
                st.success(f"Accepted match: {student_id}" if accepted else "Rejected match.")
            except (VoiceBackendUnavailable, ValueError) as exc:
                st.error(str(exc))

st.caption("Prototype notice: biometric verification requires optional dependencies. Real deployment requires consent, retention controls, access control, and anti-spoofing safeguards.")
