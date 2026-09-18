import bcrypt
import mysql.connector
import jwt

from datetime import datetime, timedelta, timezone

from database import get_connection
from config import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRE_MINUTES
from fastapi import HTTPException


def hash_password(password):
    password_bytes = password.encode("utf-8")

    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())

    return hashed.decode("utf-8")


def verify_password(plain_password, hashed_password):
    password_bytes = plain_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")

    return bcrypt.checkpw(password_bytes, hashed_bytes)


def register_user(username, password):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        password_hash = hash_password(password)

        cursor.execute(
            """
            INSERT INTO users
            (username, password_hash)
            VALUES (%s, %s)
            """,
            (username, password_hash),
        )

        connection.commit()

        return {"message": "注册成功", "username": username}

    except mysql.connector.IntegrityError:
        connection.rollback()

        raise HTTPException(status_code=409, detail="用户名已存在")

    finally:
        cursor.close()
        connection.close()


def login_user(username, password):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT id, username, password_hash
            FROM users
            WHERE username = %s
            """,
            (username,),
        )

        user = cursor.fetchone()

        if user is None:
            raise HTTPException(status_code=401, detail="用户名或密码错误")

        user_id = user[0]
        stored_username = user[1]
        stored_password_hash = user[2]

        if not verify_password(password, stored_password_hash):
            raise HTTPException(status_code=401, detail="用户名或密码错误")

        access_token = create_access_token(user_id, stored_username)

        return {
            "message": "登录成功",
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user_id,
            "username": stored_username,
        }

    finally:
        cursor.close()
        connection.close()


def create_access_token(user_id, username):
    expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)

    payload = {"user_id": user_id, "username": username, "exp": expire}

    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    return token
