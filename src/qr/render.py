"""QR image renderer kept separate from token signing."""
from io import BytesIO
import qrcode


def render_qr(token: str) -> bytes:
    image = qrcode.make(token)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()
