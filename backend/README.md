# AI Application Backend

一个基于 Python、FastAPI、MySQL、DeepSeek 和 FAISS 构建的 AI 对话后端项目。

项目主要实现用户认证、会话管理、AI 对话、对话历史、知识库上传以及基于 RAG 的知识库问答等功能。

## 项目功能

### 1. 用户认证

* 用户注册
* 用户登录
* bcrypt 密码哈希
* JWT 身份认证
* 当前用户信息查询
* 用户数据隔离

### 2. AI 对话

* 接入 DeepSeek API
* 支持多轮对话
* 保存聊天记录
* 按会话保存历史消息
* 不同用户之间的数据相互隔离

### 3. 会话管理

* 创建会话
* 获取当前用户的会话列表
* 删除会话
* 自动生成会话标题
* 删除会话时同步删除对应聊天记录

### 4. RAG 知识库

项目使用 FAISS 和 Sentence Transformers 实现向量检索。

主要流程：

```text
知识库文件
    ↓
文本提取
    ↓
文本分块
    ↓
Sentence Transformer
    ↓
向量化
    ↓
FAISS 建立索引
    ↓
用户问题向量化
    ↓
相似度检索
    ↓
获取相关知识
    ↓
DeepSeek
    ↓
生成回答
```

当前知识库包含：

* Python
* MySQL
* FastAPI
* AI

支持上传 TXT 和 PDF 文件，并在上传后重新加载知识库。

### 5. 日志与异常处理

* 统一日志记录
* 日志保存到 `logs/app.log`
* 全局异常处理
* API 异常不会直接暴露内部错误信息

## 技术栈

| 技术                    | 用途      |
| --------------------- | ------- |
| Python                | 后端开发    |
| FastAPI               | Web API |
| MySQL                 | 数据持久化   |
| DeepSeek API          | 大语言模型   |
| Sentence Transformers | 文本向量化   |
| FAISS                 | 向量检索    |
| JWT                   | 用户身份认证  |
| bcrypt                | 密码哈希    |
| Pydantic              | 请求数据校验  |

## 项目结构

```text
02-backend/
│
├── main.py                  # FastAPI API 入口
├── config.py                # 项目配置
├── database.py              # MySQL 数据库连接
│
├── auth_service.py          # 注册、登录、密码验证、JWT
├── auth_dependency.py       # JWT 身份认证依赖
│
├── chat_service.py          # AI 对话业务逻辑
├── conversation_service.py  # 会话管理
├── history_service.py       # 聊天历史
├── deepseek_service.py      # DeepSeek API
│
├── knowledge_service.py     # 知识库文件处理
├── faiss_search.py          # FAISS 向量检索
│
├── logger.py                # 日志配置
├── error_handler.py         # 全局异常处理
│
├── knowledge/               # 知识库文件
│   ├── ai.txt
│   ├── fastapi.txt
│   ├── mysql.txt
│   └── python.txt
│
├── faiss_db/                # FAISS 索引
│   ├── knowledge.index
│   └── metadata.json
│
├── logs/                    # 运行日志
│
├── .env                     # 环境变量，不提交到 Git
├── .gitignore
└── README.md
```

## API

当前主要 API：

| Method | Endpoint                           | 功能      |
| ------ | ---------------------------------- | ------- |
| POST   | `/register`                        | 用户注册    |
| POST   | `/login`                           | 用户登录    |
| GET    | `/me`                              | 获取当前用户  |
| POST   | `/chat`                            | AI 对话   |
| GET    | `/conversations`                   | 获取会话列表  |
| POST   | `/conversations`                   | 创建会话    |
| DELETE | `/conversations/{conversation_id}` | 删除会话    |
| GET    | `/chat/history/{conversation_id}`  | 获取聊天历史  |
| POST   | `/knowledge/upload`                | 上传知识库文件 |

API 文档由 FastAPI 自动生成，可以通过：

```text
http://127.0.0.1:8000/docs
```

访问 Swagger API 文档。

## 环境变量

项目使用 `.env` 保存配置。

示例：

```env
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=ai_backend

DEEPSEEK_API_KEY=your_api_key
DEEPSEEK_BASE_URL=your_base_url

JWT_SECRET_KEY=your_secret_key
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=120
```

实际使用时请填写自己的配置。


## 运行项目

安装依赖：

```powershell
pip install fastapi uvicorn mysql-connector-python python-dotenv openai PyJWT bcrypt python-multipart pypdf sentence-transformers faiss-cpu
```

启动：

```powershell
uvicorn main:app --reload
```

启动成功后访问：

```text
http://127.0.0.1:8000/docs
```

## 数据库

项目使用 MySQL 8.0。

主要数据表：

```text
users
    ↓
conversations
    ↓
chat_messages
```

其中：

* 一个用户可以拥有多个会话
* 一个会话可以拥有多条聊天记录
* 删除会话时会级联删除对应聊天记录

## Git

项目使用 Git 进行版本管理。

第一次提交：

```text
Initial commit: AI application backend
```

敏感配置、运行日志和 Python 缓存文件通过 `.gitignore` 排除。

## 项目目标

本项目用于学习和实践 AI 应用后端开发，重点覆盖：

```text
Python
  ↓
FastAPI
  ↓
MySQL
  ↓
LLM API
  ↓
RAG
  ↓
用户认证
  ↓
工程化
```

后续可以继续扩展 Agent、流式输出、Redis、Docker、测试以及部署等功能。
