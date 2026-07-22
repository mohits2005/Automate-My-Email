from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from app.core.config import settings
from fastapi.security import OAuth2PasswordBearer, oauth2, HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException
from app.database.dependencies import get_db
from app.models.user import User
from sqlalchemy.orm import Session
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
security = HTTPBearer()
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(
    plain_password: str,
    hashed_password: str
) ->bool:

    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=30)

    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm="HS256"
    )

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    
    token = credentials.credentials
    credential_exception = HTTPException(
        status_code=401,
        detail="Could not validate Credentials"
    )

    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        email = payload.get("sub")

        if email is None:
            raise credential_exception
        
    except JWTError:
        raise credential_exception
    
    user = db.query(User).filter(User.email == email).first()

    if user is None:
        raise credential_exception
    
    return user




