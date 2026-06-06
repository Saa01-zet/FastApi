from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from models import *
from utils import *

app = FastAPI()


# модели для запросов
class UserCreate(BaseModel):
    username: str
    password: str
    role: Optional[str] = "user"


class UserLogin(BaseModel):
    username: str
    password: str


# мидлваре (пункт 11)
@app.middleware("http")
async def log_middleware(request, call_next):
    print(f"{request.method} {request.url.path}")
    log(f"{request.method} {request.url.path}")
    response = await call_next(request)
    return response


# получить всех (пункт 3 - пароли скрыты)
@app.get("/users")
def get_users():
    users = load_users()
    res = []
    for u in users:
        res.append(hide_pass(u))
    return res


# получить одного
@app.get("/users/{uid}")
def get_user(uid: int):
    user = find_by_id(uid)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return hide_pass(user)


# создать пользователя (пункты 4,5,12,13,15)
@app.post("/users")
def create_user(data: UserCreate):
    # пункт 12 - защита от пустых данных
    if not not_empty(data.dict()):
        raise HTTPException(status_code=400, detail="Username и password не могут быть пустыми")

    if find_by_name(data.username):
        raise HTTPException(status_code=400, detail="Пользователь уже существует")

    # пункт 4 - проверка сложности пароля
    ok, err = check_strong(data.password)
    if not ok:
        raise HTTPException(status_code=400, detail=err)

    # пункт 5 - авто генерация ID
    uid = new_id()

    # пункт 15 - хеширование пароля
    hashed = hash_pass(data.password)

    new_user = {
        "id": uid,
        "username": data.username,
        "password": hashed,
        "role": data.role
    }

    users = load_users()
    users.append(new_user)
    save_users(users)

    log(f"Пользователь {data.username} зарегистрирован")

    return hide_pass(new_user)


# авторизация (пункт 2)
@app.post("/login")
def login(data: UserLogin):
    user = find_by_name(data.username)

    if not user or not check_pass(data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")

    log(f"Пользователь {data.username} выполнил вход")
    return {"message": "Успешный вход"}


# удаление (пункт 1)
@app.delete("/users/{uid}")
def delete_user_route(uid: int):
    user = delete_user(uid)

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    log(f"Пользователь {user['username']} удален")
    return {"message": "Пользователь удален"}


# обновление пользователя
@app.put("/users/{uid}")
def update_user(uid: int, data: UserCreate):
    user = find_by_id(uid)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if not not_empty(data.dict()):
        raise HTTPException(status_code=400, detail="Username и password не могут быть пустыми")

    ok, err = check_strong(data.password)
    if not ok:
        raise HTTPException(status_code=400, detail=err)

    users = load_users()
    for u in users:
        if u["id"] == uid:
            u["username"] = data.username
            new_hash = hash_pass(data.password)
            if u["password"] != new_hash:
                log(f"Пароль пользователя {data.username} изменен")
            u["password"] = new_hash
            u["role"] = data.role
            break

    save_users(users)
    return hide_pass(user)


# поиск (пункт 8)
@app.get("/users/search")
def search(text: str = Query(..., min_length=1)):
    found = search_by_text(text)
    res = []
    for u in found:
        res.append(hide_pass(u))
    return res


# сортировка (пункт 9)
@app.get("/users/sort")
def sort(order: str = Query("asc", regex="^(asc|desc)$")):
    sorted_users = sort_users(order)
    res = []
    for u in sorted_users:
        res.append(hide_pass(u))
    return res


# статистика (пункт 7)
@app.get("/stats")
def stats():
    return get_stats()


# запуск
if __name__ == "__main__":
    import uvicorn

    print("Сервер запущен!")
    print("http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)