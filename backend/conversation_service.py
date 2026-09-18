from database import get_connection


def create_conversation(title, user_id):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO conversations
            (title, user_id)
            VALUES (%s, %s)
            """,
            (title, user_id),
        )

        connection.commit()

        conversation_id = cursor.lastrowid

        return {"id": conversation_id, "title": title, "user_id": user_id}

    finally:
        cursor.close()
        connection.close()


def get_conversations(user_id):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT id, title, created_at
            FROM conversations
            WHERE user_id = %s
            ORDER BY created_at DESC
            """,
            (user_id,),
        )

        results = cursor.fetchall()

        conversations = []

        for row in results:
            conversations.append({"id": row[0], "title": row[1], "created_at": row[2]})

        return conversations

    finally:
        cursor.close()
        connection.close()


def check_conversation_owner(conversation_id, user_id):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT id
            FROM conversations
            WHERE id = %s
            AND user_id = %s
            """,
            (conversation_id, user_id),
        )

        conversation = cursor.fetchone()

        if conversation is None:
            return False

        return True

    finally:
        cursor.close()
        connection.close()


def delete_conversation(conversation_id, user_id):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        # 先确认这个会话属于当前用户
        cursor.execute(
            """
            SELECT id
            FROM conversations
            WHERE id = %s
            AND user_id = %s
            """,
            (conversation_id, user_id),
        )

        conversation = cursor.fetchone()

        if conversation is None:
            return False

        # 删除聊天记录
        cursor.execute(
            """
            DELETE FROM chat_messages
            WHERE conversation_id = %s
            """,
            (conversation_id,),
        )

        # 删除会话
        cursor.execute(
            """
            DELETE FROM conversations
            WHERE id = %s
            AND user_id = %s
            """,
            (conversation_id, user_id),
        )

        connection.commit()

        return True

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()
