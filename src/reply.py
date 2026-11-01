import os

from dotenv import load_dotenv

load_dotenv()


def generate_reply(client, sender, subject, body):
    user_name = os.getenv("USER_NAME")
    if not user_name:
        raise ValueError("USER_NAME is missing from .env")

    prompt = f"""
You are Hermes, an email assistant.

Write a professional reply to the following email.

The user's name is:
{user_name}

From: {sender}
Subject: {subject}

Email:
{body}

Rules:
- Be polite and professional.
- Keep the reply concise.
- Sign the email as "{user_name}".
- Never use placeholders such as [Your Name].
- Do not invent information.
- Return only the reply text.
"""

    response = client.chat.completions.create(
        model="qwen/qwen3.8-27b",
        temperature=0.2,
        messages=[{"role": "user", "content": prompt}],
    )

    return response.choices[0].message.content
