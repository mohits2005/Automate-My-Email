from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app.database.dependencies import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserLogin, Token
from app.core.security import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(tags=["Users"])

@router.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):

    existing_user = db.query(User).filter(User.email == user.email).first()

    if existing_user:
        return HTTPException(
            status_code=400,
            detail="User Already Exists",
        )
    
    new_user = User(
        name = user.name,
        email = user.email,
        hashed_password = hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login", response_model=Token)
def login(formdata: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    db_user = db.query(User).filter(
        User.email == formdata.username
    ).first()

    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or Password"
        )
    if db_user.hashed_password is None:
        raise HTTPException(
            status_code=400,
            detail="This account uses Google Sign-In. Please login with Google."
        )
    
    if not verify_password(formdata.password, db_user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or Password"
        )
    
    access_token = create_access_token(
        {
            "sub": db_user.email
        }
    )

    return{
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user 