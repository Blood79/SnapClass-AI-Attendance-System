import pytest
from src.qr.service import issue_token, verify_token

def test_qr_round_trip():
    token = issue_token({"subject_id":"abc","type":"enrollment"}, "secret", ttl_seconds=300); assert verify_token(token, "secret")["subject_id"] == "abc"

def test_qr_tamper_detection():
    token = issue_token({"subject_id":"abc"}, "secret"); raw, signature = token.split(".", 1)
    with pytest.raises(ValueError): verify_token(raw + "x." + signature, "secret")
