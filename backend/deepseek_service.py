from openai import OpenAI

from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL


client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url=DEEPSEEK_BASE_URL,
)


def ask_deepseek(messages):
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
    )

    return response.choices[0].message.content
