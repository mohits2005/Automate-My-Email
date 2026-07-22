from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from app.core.oauth import oauth
from app.core.config import settings
from app.database.dependencies import get_db
from app.models.user import User
from app.core.security import create_access_token
from datetime import datetime
from app.models.user import User
from fastapi.responses import RedirectResponse

router = APIRouter(tags=["Google OAuth"])


@router.get("/auth/google/login")
async def google_login(request: Request, frontend_redirect: str | None = None):
    if frontend_redirect:
        request.session["frontend_redirect"] = frontend_redirect
    return await oauth.google.authorize_redirect(
        request,
        settings.GOOGLE_REDIRECT_URI,
        access_type="offline",
        prompt="consent"
    )




@router.get("/auth/google/callback")
async def google_callback(
    request: Request,
    db: Session = Depends(get_db)
):
    token = await oauth.google.authorize_access_token(request)

    user_info = token["userinfo"]

    email = user_info["email"]
    name = user_info["name"]
    google_id = user_info["sub"]

    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(
            name=name,
            email=email,
            hashed_password=None,
            google_id=google_id,
            google_access_token = token["access_token"],
            google_refresh_token = token.get("refresh_token"),
            token_expiry = datetime.fromtimestamp(token["expires_at"])
            if token.get("expires_at")
            else None
        )

        db.add(user)
        db.commit()
        db.refresh(user)
    
    else:

        # Link Google account if not linked already
        if not user.google_id:
            user.google_id = google_id

        # Update latest Google tokens
        user.google_access_token = token["access_token"]

        if token.get("refresh_token"):
            user.google_refresh_token = token["refresh_token"]

        if token.get("expires_at"):
            user.token_expiry = datetime.fromtimestamp(
                token["expires_at"]
            )

        db.commit()
        db.refresh(user)

    # Generate our own JWT
    access_token = create_access_token(
        data={
            "sub": user.email
        }
    )
    frontend_redirect = request.session.pop("frontend_redirect", None)

    if frontend_redirect:

        separator = "&" if "?" in frontend_redirect else "?"

        redirect_url = (
            f"{frontend_redirect}{separator}"
            f"token={access_token}"
        )

        return RedirectResponse(url=redirect_url)

    return {
        "message": "google login successfull",
        "access_token": access_token,
        "token_type": "bearer",
        "user":{
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "google_id": user.google_id
        }
    }
    # print(user_info)

    # return user_info