from app.core.config import settings

from fastapi import FastAPI
from app.database.database import engine, Base

from app.api.email import router as email_router
from app.api.user import router as user_router
from app.models import User, Email
from app.models.email import Email
from app.models.email_analysis import EmailAnalysis
from app.api.oauth import router as oauth_router
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware

from app.services.ai_service import analyze_email
from app.api.email_analysis import router as email_analysis_router
from app.api.task import router as task_router

from app.models.task import Task


app = FastAPI(title="AI Email Workflow")
Base.metadata.create_all(bind=engine)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
app.include_router(user_router)
app.include_router(oauth_router)
app.include_router(email_router)
app.include_router(email_analysis_router)
app.include_router(task_router)

@app.get("/")
def root():
    return {
        "message": "AI Email Workflow Backend Running"
    }


# @app.get("/test-ai")
# def test_ai():

#     result = analyze_email(
#         subject="Security Alert",
#         body="""
# Google detected a login from a new device.
# Please review your account activity immediately.
# """
#     )

#     return result

