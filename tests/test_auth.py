from src.authentication.auth import hash_password, verify_password

def test_password_hash_round_trip():
    h = hash_password("correct horse battery"); assert h != "correct horse battery"; assert verify_password("correct horse battery", h); assert not verify_password("wrong password", h)
