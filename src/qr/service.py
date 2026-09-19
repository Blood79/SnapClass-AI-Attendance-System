import base64, hashlib, hmac, json, time

def _canonical(payload: dict) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()

def issue_token(payload: dict, secret: str, ttl_seconds: int = 900) -> str:
    body = dict(payload)
    body["exp"] = int(time.time()) + ttl_seconds
    raw = base64.urlsafe_b64encode(_canonical(body)).decode().rstrip("=")
    signature = hmac.new(secret.encode(), raw.encode(), hashlib.sha256).hexdigest()
    return f"{raw}.{signature}"

def verify_token(token: str, secret: str) -> dict:
    try:
        raw, signature = token.split(".", 1)
        expected = hmac.new(secret.encode(), raw.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected): raise ValueError("Invalid QR signature.")
        payload = json.loads(base64.urlsafe_b64decode(raw + "=" * (-len(raw) % 4)).decode())
        if int(payload["exp"]) < int(time.time()): raise ValueError("QR token expired.")
        return payload
    except (ValueError, KeyError, json.JSONDecodeError) as exc:
        raise ValueError("Invalid QR token.") from exc
