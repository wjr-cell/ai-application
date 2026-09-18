from database import get_connection


def get_chat_history(conversation_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, user_message, ai_reply, created_at
        FROM chat_messages
        WHERE conversation_id = %s
        ORDER BY created_at ASC
        """,
        (conversation_id,),
    )

    results = cursor.fetchall()

    cursor.close()
    connection.close()

    history = []

    for row in results:
        history.append(
            {
                "id": row[0],
                "user_message": row[1],
                "ai_reply": row[2],
                "created_at": row[3],
            }
        )

    return history
