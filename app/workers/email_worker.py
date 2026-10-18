import asyncio
import json

from app.core.redis_config import redis_client
from app.database.database import SessionLocal
from app.models.email import Email
from app.services.ai_service import analyze_email
from app.models.email_analysis import EmailAnalysis
import traceback
QUEUE = "email_analysis_queue"
PROCESSING_QUEUE = "email_analysis_processing"
FAILED_QUEUE = "email_analysis_failed"
MAX_RETRIES = 3

async def process_email(job):
    #get the first job from queue
    
    email_id = job["email_id"]
    db = SessionLocal()

    try:

        email = db.query(Email).filter(Email.id==email_id).first()

        if email is None:
            raise LookupError(f"Email with email_id: {email_id} does not exist in the database")
        

        print(f"Processing email with email id {email.id} and subject as {email.subject}")

        # result = analyze_email(subject=email.subject, body=email.body)

        analysis = db.query(EmailAnalysis).filter(EmailAnalysis.email_id==email_id).first()

        if analysis is None:
            result = analyze_email(subject=email.subject,
                                   body=email.body)
            
            analysis = EmailAnalysis(
                email_id=email_id,
                summary=result["summary"],
                priority=result["priority"],
                category=result["category"],
                action_required=result["action_required"],
                suggested_reply=result["suggested_reply"]
            )
        
            db.add(analysis)
            db.commit()
            print("COMMIT SUCCESSFUL", flush=True)
            print("Database host:", db.get_bind().url.host, flush=True)
            print("Database name:", db.get_bind().url.database, flush=True)

            print(f"AI analysis saved for email ID {email.id}", flush=True)
            print(f"AI Sucessfully Analyzed the email with email id {email.id}")
            
        else:
            print(F"Email with email id: {email_id} is already processed and saved in the database")
            return

    except Exception as e:
        db.rollback()
        print(f"Error processing the email -> {e}")
        traceback.print_exc()
        raise

    finally:
        db.close()


async def recover_processing_queue():
    recovered = 0

    while True:
        job = await redis_client.rpoplpush(PROCESSING_QUEUE, QUEUE)
        if job is None:
            break
        recovered += 1

    print(f"Recovered {recovered} no of jobs")




async def main():
    print("AUTOMATION FOR EXTRACTING TASKS, ANALYZING THEM AND SAVING IN DB HAS STARTED NOW")
    try:
        await recover_processing_queue()

        while True:
            print("Waiting for next job...", flush=True)
            try:
                job = await redis_client.brpoplpush(QUEUE, PROCESSING_QUEUE)
                print(f"Got job: {job}", flush=True)
            except Exception as e:
                print(f"Redis error while waiting for the job {e}")
                asyncio.sleep(1)
                continue

            job_data = None
            try:
                job_data = json.loads(job)
                if not isinstance(job_data, dict):
                    raise ValueError("job must be JSON object")
                email_id = job_data.get("email_id")
                if (
                    not isinstance(email_id, int)
                    or isinstance(email_id, bool)
                    or email_id <= 0):
                        raise ValueError("Job must contain a valid email_id")
                
            except (json.JSONDecodeError, ValueError, TypeError) as err:
                print(f"Invalid Job payload: {err}")
                try:
                    await redis_client.lpush(FAILED_QUEUE, job)
                except Exception as e:
                    print(f"Could not move invalid job into a queue {e}")
                    continue
                else:
                    await redis_client.lrem(PROCESSING_QUEUE, 1, job)
                    continue
            try:
                await process_email(job_data)

            except Exception as e:
                print(f"Job failed with error: {e}")

                try:
                    attempts = job_data.get("attempts", 0) + 1
                    job_data["attempts"] = attempts
                    updated_job = json.dumps(job_data)

                    if attempts < MAX_RETRIES:
                        await redis_client.lpush(QUEUE, updated_job)

                        print(f"Retrying email with email_id: {job_data.get('email_id')} {attempts}/{MAX_RETRIES - 1}")

                    else:
                        await redis_client.lpush(FAILED_QUEUE, updated_job)
                        print(f"Job {email_id} moved to failed queue")

                except Exception as e:
                    print(f"Could not schedule retry {e}")
                    continue

            
            await redis_client.lrem(PROCESSING_QUEUE, 1, job)
            continue
    finally:
        await redis_client.aclose()

print("WORKER FILE LOADED", flush=True)

try:
    print("ABOUT TO START MAIN", flush=True)
    asyncio.run(main())
except KeyboardInterrupt:
    print("Worker interrupted", flush=True)
except Exception as e:
    print(f"WORKER CRASHED: {e}", flush=True)
    traceback.print_exc()


                







#asyncio.run(process_email())