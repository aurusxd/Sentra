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

def build_user_promt(
    question: str,
    post: str,
    description: str, 
    instruction: str, 
    tone: str, 
    context: str, 
    fallback: str):
    return f"""
    Ты - сотрудник {post} бизнеса: {description}.
    Соблюдай эти инструкции: {instruction} и отвечай в {tone} тоне.
    Отвечай строго по этому контексту: {context}.
    Если не знаешь или не уверен в ответе, отвечай: {fallback}

    Вопрос:{question}
    """


async def ask_agent(
    question: str,
    post: str,
    description: str, 
    instruction: str, 
    tone: str, 
    context: str, 
    fallback: str
):
    messages = [
        {
            "role": "system",
            "content": system_prompt

        },
        {
            "role": "user",
            "content": build_user_promt(
                question=question,
                post=post,
                description=description,
                instruction=instruction,
                tone=tone,
                context=context,
                fallback=fallback
                
            ),
        },
    ]

    try:
        first_response = client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=messages,
        )

        message = first_response.choices[0].message


        messages.append(message)

        return message
    except Exception:
        log.exception("Message not created")


    
    

