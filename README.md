# AI Application Platform

一个基于 FastAPI、MySQL、DeepSeek、RAG 和 FAISS 构建的 AI 对话应用。

项目实现了从用户注册登录、会话管理、知识库上传，到基于知识库的 AI 问答的完整流程，并通过前后端分离的方式组织项目结构。

## 项目功能

### 1. 用户认证

- 用户注册
- 用户登录
- bcrypt 密码哈希
- JWT 身份认证
- 用户信息获取
- 用户数据隔离

### 2. AI 对话

- DeepSeek API 接入
- 多轮上下文对话
- 对话记录持久化
- 多会话管理
- 创建会话
- 删除会话
- 查询历史消息

### 3. RAG 知识库

- TXT 知识库
- PDF 知识库
- 文档自动解析
- 文档分块
- Sentence Transformers 向量化
- FAISS 向量检索
- 相似度检索
- 根据检索结果生成回答
- 返回知识来源

### 4. 知识库动态更新

用户可以通过前端上传新的 TXT 或 PDF 文件。

上传流程：

```text
上传文件
    ↓
文件解析
    ↓
保存知识文件
    ↓
文本分块
    ↓
向量化
    ↓
更新 FAISS 索引
    ↓
重新加载知识库

无需手动重新启动后端即可使用新知识。

5. 后端工程化
FastAPI
MySQL
JWT Authentication
bcrypt
Pydantic
CORS
日志系统
全局异常处理
模块化代码结构
配置文件与环境变量管理
技术栈
类型	技术
编程语言	Python
后端框架	FastAPI
数据库	MySQL 8.0
大语言模型	DeepSeek
Embedding	Sentence Transformers
向量数据库	FAISS
身份认证	JWT
密码安全	bcrypt
API 文档	Swagger / OpenAPI
前端	HTML / CSS / JavaScript
版本控制	Git / GitHub
系统架构
                    ┌─────────────────────┐
                    │      Frontend       │
                    │   HTML/CSS/JS       │
                    └──────────┬──────────┘
                               │ HTTP
                               ↓
                    ┌─────────────────────┐
                    │       FastAPI       │
                    │      Backend        │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ↓                ↓                ↓
       ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
       │    MySQL    │  │   DeepSeek  │  │    FAISS    │
       │             │  │     LLM     │  │ Vector Index│
       └─────────────┘  └─────────────┘  └──────┬──────┘
                                                 │
                                                 ↓
                                        ┌────────────────┐
                                        │ Knowledge Base │
                                        │ TXT / PDF      │
                                        └────────────────┘
RAG 工作流程
用户问题
   ↓
文本向量化
   ↓
FAISS 相似度搜索
   ↓
获取相关知识
   ↓
构造 Prompt
   ↓
DeepSeek
   ↓
生成回答
   ↓
返回回答 + 知识来源

当知识库中不存在与问题相关的信息时，系统不会直接使用通用模型回答，而是返回知识库中没有找到相关信息。

项目结构
ai-application/
│
├── backend/
│   │
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   │
│   ├── auth_service.py
│   ├── auth_dependency.py
│   │
│   ├── chat_service.py
│   ├── conversation_service.py
│   ├── history_service.py
│   │
│   ├── deepseek_service.py
│   ├── faiss_search.py
│   ├── knowledge_service.py
│   │
│   ├── logger.py
│   ├── error_handler.py
│   │
│   ├── knowledge/
│   │   ├── ai.txt
│   │   ├── python.txt
│   │   ├── mysql.txt
│   │   └── fastapi.txt
│   │
│   ├── faiss_db/
│   │   ├── knowledge.index
│   │   └── metadata.json
│   │
│   └── README.md
│
├── frontend/
│   ├── index.html
│   └── .gitignore
│
├── .gitignore
└── README.md
API

主要 API：

Method	Endpoint	功能
POST	/register	用户注册
POST	/login	用户登录
GET	/me	获取当前用户
POST	/chat	AI 对话
GET	/conversations	获取会话列表
POST	/conversations	创建会话
DELETE	/conversations/{id}	删除会话
GET	/chat/history/{id}	获取聊天历史
POST	/knowledge/upload	上传知识库

API 文档可以通过 FastAPI 自动生成的 Swagger 页面查看：

http://127.0.0.1:8000/docs
数据库设计

系统主要使用两个核心业务表：

users

保存用户认证信息。

users
├── id
├── username
└── password_hash
conversations

保存用户的对话。

conversations
├── id
├── title
├── created_at
└── user_id
chat_messages

保存具体聊天消息。

chat_messages
├── id
├── user_message
├── ai_reply
├── created_at
└── conversation_id

其中：

users
   │
   └── conversations
           │
           └── chat_messages

通过用户 ID 和会话 ID 实现不同用户之间的数据隔离。

安全设计

项目使用 JWT 对 API 请求进行身份认证。

登录成功后：

用户名 + 密码
      ↓
bcrypt 验证
      ↓
生成 JWT
      ↓
前端保存 Token
      ↓
后续 API 请求携带 Authorization
      ↓
后端验证 JWT

密码不会以明文形式存储在数据库中。

敏感配置通过 .env 管理：

MYSQL_PASSWORD
DEEPSEEK_API_KEY
JWT_SECRET_KEY

.env 不提交到 Git。

异常处理与日志

项目实现了统一异常处理机制。

发生未处理异常时：

API Request
     ↓
Exception
     ↓
Global Exception Handler
     ↓
记录日志
     ↓
返回统一错误信息

日志文件：

logs/app.log

敏感信息不会写入日志。

运行项目
1. 安装 Python 依赖

进入后端目录：

cd backend

安装依赖：

pip install fastapi uvicorn mysql-connector-python openai python-dotenv python-multipart pypdf sentence-transformers faiss-cpu bcrypt PyJWT
2. 配置环境变量

在 backend 目录创建：

.env

配置：

MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=你的MySQL密码
MYSQL_DATABASE=ai_backend

DEEPSEEK_API_KEY=你的DeepSeek API Key
DEEPSEEK_BASE_URL=你的DeepSeek API地址

JWT_SECRET_KEY=你的JWT密钥
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=120
3. 启动后端
uvicorn main:app --reload

启动后访问：

http://127.0.0.1:8000/docs
4. 启动前端

使用浏览器打开：

frontend/index.html

或者使用 VS Code Live Server 等静态服务器运行前端页面。

当前实现

目前项目已经实现：

用户注册
用户登录
JWT 身份认证
用户数据隔离
DeepSeek AI 对话
多轮上下文
多会话管理
聊天历史
TXT 知识库
PDF 知识库
Sentence Transformer 向量化
FAISS 向量检索
RAG 问答
知识来源展示
动态知识库更新
日志系统
全局异常处理
前后端分离
Git / GitHub 版本管理
后续计划

后续可以进一步完善：

Streaming 流式输出
Agent 工具调用
更完善的权限管理
更复杂的知识库管理
文件删除与知识库维护
Docker 部署
Linux 服务器部署
自动化测试
CI/CD
项目定位

这是一个面向 AI 应用开发场景的全栈项目，重点实践：

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
Vector Search
  ↓
Authentication
  ↓
Frontend

通过该项目实践 AI 应用从 API 调用、后端开发、数据库设计，到 RAG、身份认证和前后端整合的完整开发流程。