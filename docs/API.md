# API surface

The important interfaces are framework-independent:

- src.qr.service.issue_token / verify_token
- src.attendance.service.AttendanceRecord / attendance_rate
- src.authentication.auth.hash_password / verify_password
- src.computer_vision.face.FaceVerifier
- src.voice.recognizer.VoiceRecognizer

The Flask app is intentionally a landing page rather than an unauthenticated attendance API. A future REST layer can expose these services without moving business rules into the web framework.
