from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database.dependencies import get_db
from app.models.task import Task
from app.schemas.task import TaskResponse, TaskStatusUpdate
from app.core.security import get_current_user

from app.models.email import Email
from app.models.email_analysis import EmailAnalysis
from app.schemas.dashboard import DashboardResponse

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)

@router.get(
    "/",
    response_model=List[TaskResponse]
)
def get_tasks(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    tasks = (
        db.query(Task)
        .join(Task.email)
        .filter(Task.email.has(user_id=current_user.id))
        .all()
    )

    return tasks

@router.get(
    "/dashboard",
    response_model=DashboardResponse
)
def dashboard(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    total_emails = db.query(Email).filter(
        Email.user_id == current_user.id
    ).count()

    analyzed_emails = (
        db.query(EmailAnalysis)
        .join(Email)
        .filter(Email.user_id == current_user.id)
        .count()
    )

    total_tasks = (
        db.query(Task)
        .join(Task.email)
        .filter(Task.email.has(user_id=current_user.id))
        .count()
    )

    pending_tasks = (
        db.query(Task)
        .join(Task.email)
        .filter(
            Task.email.has(user_id=current_user.id),
            Task.status == "Pending"
        )
        .count()
    )

    completed_tasks = (
        db.query(Task)
        .join(Task.email)
        .filter(
            Task.email.has(user_id=current_user.id),
            Task.status == "Completed"
        )
        .count()
    )

    high_priority_emails = (
        db.query(EmailAnalysis)
        .join(Email)
        .filter(
            Email.user_id == current_user.id,
            EmailAnalysis.priority == "High"
        )
        .count()
    )

    return DashboardResponse(
        total_emails=total_emails,
        analyzed_emails=analyzed_emails,
        total_tasks=total_tasks,
        pending_tasks=pending_tasks,
        completed_tasks=completed_tasks,
        high_priority_emails=high_priority_emails
    )

@router.get(
    "/{task_id}",
    response_model=TaskResponse
)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    task = (
        db.query(Task)
        .join(Task.email)
        .filter(
            Task.id == task_id,
            Task.email.has(user_id=current_user.id)
        )
        .first()
    )

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found."
        )

    return task

@router.patch(
    "/{task_id}",
    response_model=TaskResponse
)
def update_task_status(
    task_id: int,
    task_update: TaskStatusUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    # Find the task belonging to the current user
    task = (
        db.query(Task)
        .join(Task.email)
        .filter(
            Task.id == task_id,
            Task.email.has(user_id=current_user.id)
        )
        .first()
    )

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found."
        )

    # Validate status
    if task_update.status not in ["Pending", "Completed"]:
        raise HTTPException(
            status_code=400,
            detail="Status must be either 'Pending' or 'Completed'."
        )

    # Update status
    task.status = task_update.status

    db.commit()
    db.refresh(task)

    return task

@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    task = (
        db.query(Task)
        .join(Task.email)
        .filter(
            Task.id == task_id,
            Task.email.has(user_id=current_user.id)
        )
        .first()
    )

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found."
        )

    db.delete(task)
    db.commit()

    return {
        "message": "Task deleted successfully."
    }


