import json
from app.core.redis_config import redis_client


EMAIL_ANALYSIS_QUEUE = "email_analysis_queue"

async def enqueue_email_analysis(email_id: int):

    job = {
        "email_id": email_id
    }

    await redis_client.rpush(EMAIL_ANALYSIS_QUEUE, json.dumps(job))

