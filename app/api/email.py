import base64
from email.utils import parsedate_to_datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from app.database.dependencies import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.email import Email


router = APIRouter(
    tags=["Emails"]
)

@router.get("/emails")
def list_emails(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    emails = (
        db.query(Email)
        .filter(Email.user_id == current_user.id)
        .order_by(Email.id.desc())
        .all()
    )

    return [
        {
            "id": e.id,
            "sender": e.sender,
            "recipent": e.recipent,
            "subject": e.subject,
            "body": e.body,
            "recieved_at": e.recieved_at,
            "processed": e.processed,
            "analysis": {
                "summary": e.analysis.summary,
                "priority": e.analysis.priority,
                "category": e.analysis.category,
                "action_required": e.analysis.action_required,
                "suggested_reply": e.analysis.suggested_reply
            } if e.analysis else None
        }
        for e in emails
    ]


def extract_email_body(payload):

    if "parts" in payload:

        for part in payload["parts"]:

            if part["mimeType"] == "text/plain":

                data = part["body"].get("data")

                if data:

                    return base64.urlsafe_b64decode(
                        data
                    ).decode("utf-8")

    else:

        data = payload["body"].get("data")

        if data:

            return base64.urlsafe_b64decode(
                data
            ).decode("utf-8")

    return ""


def get_header(headers, name):

    for header in headers:

        if header["name"] == name:

            return header["value"]

    return ""


@router.get("/emails/sync")
def sync_emails(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # Check whether the user has connected a Google account
    if not current_user.google_access_token:

        raise HTTPException(
            status_code=400,
            detail="Google account not connected."
        )

    # Create Google credentials using the stored access token
    credentials = Credentials(
        token=current_user.google_access_token
    )

    # Build Gmail API service
    service = build(
        "gmail",
        "v1",
        credentials=credentials
    )

    # Fetch the latest 10 email IDs
    results = service.users().messages().list(
        userId="me",
        maxResults=10
    ).execute()

    messages = results.get("messages", [])

    if not messages:

        return {
            "message": "No emails found."
        }

    synced = []

    for message in messages:

        # Fetch complete email details
        gmail_message = service.users().messages().get(
            userId="me",
            id=message["id"],
            format="full"
        ).execute()

        # Skip duplicate emails
        existing = db.query(Email).filter(
            Email.gmail_message_id == message["id"]
        ).first()

        if existing:
            continue

        payload = gmail_message["payload"]

        headers = payload["headers"]

        sender = get_header(headers, "From")
        recipient = get_header(headers, "To")
        subject = get_header(headers, "Subject")
        date = get_header(headers, "Date")

        received_at = None

        if date:

            try:
                received_at = parsedate_to_datetime(date)
            except:
                pass

        body = extract_email_body(payload)

        email = Email(
            user_id=current_user.id,
            gmail_message_id=message["id"],
            sender=sender,
            recipent=recipient,
            subject=subject,
            body=body,
            recieved_at=received_at,
            processed=False
        )

        db.add(email)

        synced.append(subject)

    db.commit()

    return {
        "message": "Emails synced successfully.",
        "total_synced": len(synced),
        "emails": synced
    }