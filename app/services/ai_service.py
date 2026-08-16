import json

from groq import Groq

from app.core.config import settings


client = Groq(
    api_key=settings.GROQ_API_KEY
)


def analyze_email(subject: str, body: str):

    prompt = f"""
You are an AI Email Assistant.

Analyze the email below.

Return ONLY valid JSON.

{{
    "summary": "",
    "priority": "HIGH | MEDIUM | LOW",
    "category": "",
    "action_required": "YES | NO",
    "suggested_reply": ""
}}

Email Subject:
{subject}

Email Body:
{body}
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.2
    )

    result = response.choices[0].message.content

    result = result.strip()

    if result.startswith("```"):
        result = result.replace("```json", "")
        result = result.replace("```", "")
        result = result.strip()

    return json.loads(result)

def generate_reply(subject: str, body: str):

    prompt = f"""
You are a professional email assistant.

Write a polite, professional reply to the following email.

Subject:
{subject}

Email:
{body}

Rules:
- Return ONLY the reply.
- Do not explain anything.
- Do not use markdown.
- Keep the tone professional.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.4
    )

    return response.choices[0].message.content.strip()

def extract_tasks(subject: str, body: str):

    prompt = f"""
You are an AI assistant.

Extract all actionable tasks from the email.

Return ONLY valid JSON.

Format:

{{
    "tasks": [
        {{
            "task": "Task description",
            "deadline": "Deadline if mentioned, otherwise 'Not specified'"
        }}
    ]
}}

Subject:
{subject}

Email:
{body}

If there are no actionable tasks, return:

{{
    "tasks": []
}}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2
    )

    result = response.choices[0].message.content

    result = result.strip()

    if result.startswith("```"):
        result = result.replace("```json", "")
        result = result.replace("```", "")
        result = result.strip()

    return json.loads(result)
