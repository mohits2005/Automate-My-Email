from app.core.redis_config import redis_client
import asyncio
import os
from dotenv import load_dotenv
import json
load_dotenv()
# async def main():
    
#     await redis_client.set("name", "Mohit Sharma")

#     value = await redis_client.get("name")

#     print("Redis's response", value)

#     await redis_client.delete("name")

#     await redis_client.aclose()

# asyncio.run(main())


# url = os.getenv("REDIS_UPSTASH_URL")

# print(url)

from app.core.redis_config import redis_client

QUEUE = "email_analysis_queue"

async def main():

    length = await redis_client.llen(QUEUE)

    print("The current length of the queue is:", length)

    if length > 0:
        job = await redis_client.lindex(QUEUE, 0)

        print("Job at index 0 is:", json.loads(job))


    await redis_client.aclose()

asyncio.run(main())
