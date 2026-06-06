import hashlib
from datetime import datetime

def hash_pass(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()[:10]

def log(msg):
    with open("logs.txt", "a", encoding="utf-8") as f:
        t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{t}] {msg}\n")

def check_pass(pwd, hashed):
    return hash_pass(pwd) == hashed

def check_strong(pwd):
    if len(pwd) < 6:
        return False, "Слишком простой пароль"
    if pwd.isdigit():
        return False, "Слишком простой пароль"
    return True, ""

def not_empty(data):
    if data is None:
        return False
    if "username" not in data or "password" not in data:
        return False
    if data["username"] == "" or data["username"].strip() == "":
        return False
    if data["password"] == "":
        return False
    return True

def hide_pass(user):
    return {
        "id": user["id"],
        "username": user["username"],
        "role": user.get("role", "user")
    }