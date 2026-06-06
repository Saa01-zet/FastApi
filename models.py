import json
import os
import hashlib

USER_FILE = "users.json"

def hash_pass(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()[:10]

def load_users():
    if not os.path.exists(USER_FILE):
        users = [
            {"id": 1, "username": "alex", "password": hash_pass("123456"), "role": "admin"},
            {"id": 2, "username": "john", "password": hash_pass("password123"), "role": "user"},
            {"id": 3, "username": "alexander", "password": hash_pass("qwerty123"), "role": "user"}
        ]
        save_users(users)
        return users
    with open(USER_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_users(users):
    with open(USER_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def find_by_id(uid):
    users = load_users()
    for u in users:
        if u["id"] == uid:
            return u
    return None

def find_by_name(name):
    users = load_users()
    for u in users:
        if u["username"] == name:
            return u
    return None

def new_id():
    users = load_users()
    if len(users) == 0:
        return 1
    maxid = users[0]["id"]
    for u in users:
        if u["id"] > maxid:
            maxid = u["id"]
    return maxid + 1

def delete_user(uid):
    users = load_users()
    for i in range(len(users)):
        if users[i]["id"] == uid:
            user = users[i]
            users.pop(i)
            save_users(users)
            return user
    return None

def search_by_text(text):
    users = load_users()
    res = []
    text = text.lower()
    for u in users:
        if text in u["username"].lower():
            res.append(u)
    return res

def sort_users(order):
    users = load_users()
    n = len(users)
    for i in range(n):
        for j in range(0, n-i-1):
            if order == "asc":
                if users[j]["username"] > users[j+1]["username"]:
                    users[j], users[j+1] = users[j+1], users[j]
            else:
                if users[j]["username"] < users[j+1]["username"]:
                    users[j], users[j+1] = users[j+1], users[j]
    return users

def get_stats():
    users = load_users()
    if len(users) == 0:
        return {"users_count": 0, "longest_username": ""}
    longest = users[0]["username"]
    for u in users:
        if len(u["username"]) > len(longest):
            longest = u["username"]
    return {"users_count": len(users), "longest_username": longest}