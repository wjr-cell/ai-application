from database import get_connection
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator

from knowledge_service import upload_knowledge_file
from chat_service import chat_with_knowledge
from conversation_service import (
    create_conversation,
    get_conversations,
    check_conversation_owner,
    delete_conversation,
)
from history_service import get_chat_history
from error_handler import global_exception_handler
from auth_service import register_user, login_user
from auth_dependency import get_current_user


app = FastAPI()

app.add_exception_handler(Exception, global_exception_handler)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ConversationCreate(BaseModel):
    title: str


class RegisterRequest(BaseModel):
    username: str

    password: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, value):
        value = value.strip()

        if not value:
            raise ValueError("用户名不能为空")

        if len(value) < 3:
            raise ValueError("用户名至少需要3个字符")

        if len(value) > 50:
            raise ValueError("用户名不能超过50个字符")

        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        if len(value) < 6:
            raise ValueError("密码至少需要6个字符")

        if len(value) > 100:
            raise ValueError("密码不能超过100个字符")

        return value


class LoginRequest(BaseModel):
    username: str

    password: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, value):
        value = value.strip()

        if not value:
            raise ValueError("用户名不能为空")

        return value


class ChatRequest(BaseModel):
    conversation_id: int
    message: str


@app.post("/register")
def register(data: RegisterRequest):
    return register_user(data.username, data.password)


@app.post("/login")
def login(data: LoginRequest):
    return login_user(data.username, data.password)


@app.post("/knowledge/upload")
async def upload_knowledge(
    file: UploadFile = File(...), current_user: dict = Depends(get_current_user)
):
    content = await file.read()

    result = upload_knowledge_file(content, file.filename)

    return result


# AI聊天
@app.post("/chat")
def chat(data: ChatRequest, current_user: dict = Depends(get_current_user)):
    is_owner = check_conversation_owner(data.conversation_id, current_user["user_id"])

    if not is_owner:
        raise HTTPException(status_code=403, detail="无权访问该会话")

    return chat_with_knowledge(data.conversation_id, data.message)


@app.post("/conversations")
def create_conversation_api(
    data: ConversationCreate, current_user: dict = Depends(get_current_user)
):
    return create_conversation(data.title, current_user["user_id"])


@app.get("/conversations")
def get_conversations_api(current_user: dict = Depends(get_current_user)):
    return get_conversations(current_user["user_id"])


@app.delete("/conversations/{conversation_id}")
def delete_conversation_api(
    conversation_id: int, current_user: dict = Depends(get_current_user)
):
    success = delete_conversation(conversation_id, current_user["user_id"])

    if not success:
        raise HTTPException(status_code=404, detail="会话不存在或无权删除")

    return {"message": "会话删除成功"}


@app.get("/chat/history/{conversation_id}")
def get_chat_history_api(
    conversation_id: int, current_user: dict = Depends(get_current_user)
):
    is_owner = check_conversation_owner(conversation_id, current_user["user_id"])

    if not is_owner:
        raise HTTPException(status_code=403, detail="无权访问该会话")

    return get_chat_history(conversation_id)


@app.get("/me")
def get_me(current_user: dict = Depends(get_current_user)):
    return current_user
