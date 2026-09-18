from database import get_connection
from deepseek_service import ask_deepseek
from faiss_search import search_knowledge
from logger import logger


def chat_with_knowledge(conversation_id, user_message):
    logger.info(f"收到聊天请求 conversation_id={conversation_id}")

    connection = get_connection()
    cursor = connection.cursor()

    # 查询历史消息
    cursor.execute(
        """
        SELECT user_message, ai_reply
        FROM chat_messages
        WHERE conversation_id = %s
        ORDER BY created_at DESC
        LIMIT 10
        """,
        (conversation_id,),
    )

    results = cursor.fetchall()

    # 构造对话上下文
    messages = [
        {
            "role": "system",
            "content": "你是一个友好的AI助手。请根据聊天上下文回答用户的问题。",
        }
    ]

    for row in reversed(results):
        messages.append({"role": "user", "content": row[0]})

        messages.append({"role": "assistant", "content": row[1]})

    # RAG 检索
    rag_results = search_knowledge(user_message)
    logger.info(f"RAG 检索完成，找到 {len(rag_results)} 个相关知识块")

    knowledge = ""

    for item in rag_results:
        knowledge += item["content"] + "\n"

    # 没有相关知识
    if not knowledge:
        reply = "抱歉，我在当前知识库中没有找到与这个问题相关的信息。"

    else:
        messages.append(
            {
                "role": "system",
                "content": f"""
你是一个知识库问答助手。

请严格根据下面提供的知识库内容回答用户的问题。

知识库内容：
{knowledge}

要求：
1. 只能使用知识库中提供的信息回答。
2. 不要使用知识库之外的知识补充答案。
3. 如果知识库内容不足以回答问题，请明确说明知识库中的信息不足。
4. 可以对知识库内容进行解释，但不要编造新的事实。
""",
            }
        )

        messages.append({"role": "user", "content": user_message})
        logger.info("开始调用 DeepSeek")
        reply = ask_deepseek(messages)

    # 保存聊天记录
    cursor.execute(
        """
        INSERT INTO chat_messages
        (conversation_id, user_message, ai_reply)
        VALUES (%s, %s, %s)
        """,
        (conversation_id, user_message, reply),
    )

    # 自动生成会话标题
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM chat_messages
        WHERE conversation_id = %s
        """,
        (conversation_id,),
    )

    message_count = cursor.fetchone()[0]

    if message_count == 1:
        title = user_message[:30]

        cursor.execute(
            """
            UPDATE conversations
            SET title = %s
            WHERE id = %s
            """,
            (title, conversation_id),
        )

    connection.commit()

    cursor.close()
    connection.close()
    logger.info(f"聊天处理完成 conversation_id={conversation_id}")

    return {"reply": reply, "sources": rag_results}
