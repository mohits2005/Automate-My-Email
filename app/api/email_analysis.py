from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.dependencies import get_db

from app.core.security import get_current_user

from app.models.email import Email
from app.models.email_analysis import EmailAnalysis

from app.schemas.email_analysis import EmailAnalysisResponse

from app.services.ai_service import analyze_email
from app.schemas.email_reply import EmailReplyResponse
from app.services.ai_service import generate_reply

from app.schemas.email_task import EmailTaskResponse
from app.services.ai_service import extract_tasks
from app.models.task import Task

router = APIRouter(
    prefix="/emails",
    tags=["Email Analysis"]
)

@router.post(
    "/{email_id}/reply",
    response_model=EmailReplyResponse
)
def generate_reply_endpoint(
    email_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    # Find email
    email = db.query(Email).filter(
        Email.id == email_id
    ).first()

    if not email:
        raise HTTPException(
            status_code=404,
            detail="Email not found."
        )

    # Ownership check
    if email.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized."
        )

    # Generate reply
    reply = generate_reply(
        subject=email.subject,
        body=email.body
    )

    return EmailReplyResponse(
        email_id=email.id,
        reply=reply
    )


@router.post(
    "/{email_id}/analyze",
    response_model=EmailAnalysisResponse
)
def analyze_email_endpoint(
    email_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    email = db.query(Email).filter(
        Email.id == email_id
    ).first()

    if not email:
        raise HTTPException(
            status_code=404,
            detail="Email not found."
        )

    if email.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized."
        )
    
    existing_analysis = db.query(EmailAnalysis).filter(
        EmailAnalysis.email_id == email.id
    ).first()

    if existing_analysis:
        return existing_analysis
    
    analysis = analyze_email(
        subject=email.subject,
        body=email.body
    )

    
    email_analysis = EmailAnalysis(
        email_id=email.id,
        summary=analysis["summary"],
        priority=analysis["priority"],
        category=analysis["category"],
        action_required=analysis["action_required"],
        suggested_reply=analysis["suggested_reply"]
    )

    db.add(email_analysis)
    db.commit()
    db.refresh(email_analysis)

    return email_analysis

@router.post(
    "/{email_id}/tasks",
    response_model=EmailTaskResponse
)
def extract_tasks_endpoint(
    email_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    # Step 1: Find Email
    email = db.query(Email).filter(
        Email.id == email_id
    ).first()

    if not email:
        raise HTTPException(
            status_code=404,
            detail="Email not found."
        )

    # Step 2: Check Ownership
    if email.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized."
        )

    # Step 3: Check if tasks already exist
    existing_tasks = db.query(Task).filter(
        Task.email_id == email.id
    ).all()

    if existing_tasks:
        return EmailTaskResponse(
            email_id=email.id,
            tasks=[
                {
                    "task": task.task,
                    "deadline": task.deadline
                }
                for task in existing_tasks
            ]
        )

    # Step 4: Extract tasks using AI
    extracted_tasks = extract_tasks(
        subject=email.subject,
        body=email.body
    )

    # Step 5: Save tasks into database
    for item in extracted_tasks["tasks"]:

        new_task = Task(
            email_id=email.id,
            task=item["task"],
            deadline=item["deadline"]
        )

        db.add(new_task)

    db.commit()

    # Step 6: Return extracted tasks
    return EmailTaskResponse(
        email_id=email.id,
        tasks=extracted_tasks["tasks"]
    )