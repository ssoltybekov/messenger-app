import bcrypt

def hash_password(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(pwd_bytes, salt)
    return hashed_password.decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    password_bytes = password.encode('utf-8')
    hashed_bytes = hashed.encode('utf-8')

    return bcrypt.checkpw(password_bytes, hashed_bytes)