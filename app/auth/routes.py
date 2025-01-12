from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from datetime import timedelta
import json
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from app.db.session import SessionLocal
from app.auth.models import User
from app.auth.models import EnvelopData 
from app.auth.utils import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
)
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.schemas.user import EnvelopDataResponse, EnvelopeCreate 
from app.config import settings
from sqlalchemy.dialects import postgresql

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login") 



def get_current_user_id(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id")
        print("user id", user_id)
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing user_id in token",
            )
        return user_id
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
        )

@router.post("/signup", response_model=UserResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    print("Received JSON Payload:", json.dumps(user.dict(), indent=2))
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    new_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        hashed_password=hash_password(user.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login")
def login(user: UserLogin, response: Response, db: Session = Depends(get_db)):
    print("Received JSON Payload:", json.dumps(user.dict(), indent=2))
    
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials")
    
    access_token = create_access_token(
        data={"sub": db_user.email, "user_id": db_user.user_id, "first_name": db_user.first_name},
        expires_delta=timedelta(minutes=30)
    )
    refresh_token = create_refresh_token(data={"sub": db_user.email})
    
    response.set_cookie(key="user_id", value=db_user.user_id, httponly=True, secure=True, samesite="strict")
    response.set_cookie(key="first_name", value=db_user.first_name, httponly=True, secure=True, samesite="strict")
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, secure=True, samesite="strict")
    
    return {"access_token": access_token, "token_type": "bearer", "name": db_user.first_name}

@router.post("/refresh")
def refresh(response: Response, refresh_token: str = Depends(verify_refresh_token)):
    access_token = create_access_token(data={"sub": refresh_token["sub"]}, expires_delta=timedelta(minutes=30))
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/envelopes", response_model=list[EnvelopDataResponse])
def get_envelopes(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
    ):
    print("Entering /envelopes endpoint")
    user_id = get_current_user_id(token)
    print(f"Decoded user_id from token: {user_id}")
    envelopes_query = db.query(EnvelopData).filter(EnvelopData.user_id == user_id)
    print("SQL Query: ", str(envelopes_query.statement.compile(dialect=postgresql.dialect())))
    envelopes = envelopes_query.all()    
    print(f"Envelopes found: {envelopes}")
    if not envelopes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No envelopes found for the user",
        )
    return envelopes

@router.post("/add-envelope", response_model=EnvelopDataResponse)
def add_envelope(
    envelope: EnvelopeCreate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    user_id = get_current_user_id(token)  
    print(f"Adding envelope for user_id: {user_id}")
    
   
    existing_envelope = db.query(EnvelopData).filter(
        EnvelopData.user_id == user_id, 
        EnvelopData.envelope_name == envelope.envelope_name
    ).first()
    if existing_envelope:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Envelope already exists for this user with the same name"
        )
    
    
    new_envelope = EnvelopData(
        user_id=user_id,
        envelope_name=envelope.envelope_name,
        initial_amount=envelope.initial_amount,
        remaining_amount=envelope.initial_amount,  
    )
    
    db.add(new_envelope)
    db.commit()
    db.refresh(new_envelope)
    
    
    return new_envelope
