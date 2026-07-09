import json
import os

from dotenv import load_dotenv
from openai import OpenAI
from backend.utils.logger import log

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)


system_prompt ="""

"""

def build_user_promt(post: str,description: str, instucrtion: str, tone: str, context: str, fallback: str):
    return f"""
    Ты - сотрудник {post} бизнеса: {description}.
    Соблюдай эти инструкции: {instucrtion} и отвечай в {tone} тоне.
    Отвечай строго по этому контексту: {context}.
    Если не знаешь или не уверен в ответе, отвечай: {fallback}
    """


async def ask_agent(
    user_topic: str,
    description: str,
):
    messages = [
        {
            "role": "system",
            "content": system_prompt

        },
        {
            "role": "user",
            "content": build_user_promt(user_topic,description),
        },
    ]

    first_response = client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=messages,
    )

    message = first_response.choices[0].message


    messages.append(message)



    return message


    
    

