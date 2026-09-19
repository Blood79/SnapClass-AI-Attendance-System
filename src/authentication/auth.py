from enum import Enum
import bcrypt

class Role(str, Enum):
    TEACHER = "teacher"
    STUDENT = "student"
    ADMIN = "admin"

def hash_password(password: str) -> str:
    if len(password) < 8:
        raise ValueError("Password must contain at least 8 characters.")
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), password_hash.encode())
    except (ValueError, TypeError):
        return False

def can_access(user_role: str, *allowed: Role) -> bool:
    return user_role in {role.value for role in allowed}
