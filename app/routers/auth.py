#from fastapi import APIRouter, Depends, HTTPException
#from sqlalchemy.orm import Session
#from app.core.database import get_db
#from app.schemas.schemas import UserCreate, UserLogin, UserResponse
#from app.repositories.crud import create_user, authenticate_user
#from app.core.security import create_access_token
#
#router = APIRouter(prefix="/auth", tags=["Auth"])
#
#@router.post("/register", response_model=UserResponse)
#def register(user: UserCreate, db: Session = Depends(get_db)):
#    existing = authenticate_user(db, user.email, user.password)
#    if existing:
#        raise HTTPException(status_code=400, detail="User already exists")
#
#    new_user = create_user(db, user.email, user.password)
#    return new_user
#
#@router.post("/login")
#def login(user: UserLogin, db: Session = Depends(get_db)):
#    auth_user = authenticate_user(db, user.email, user.password)
#    if not auth_user:
#        raise HTTPException(status_code=401, detail="Invalid credentials")
#
#    token = create_access_token({"user_id": auth_user.id})
#    return {"access_token": token, "token_type": "bearer"}


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.schemas import UserCreate, UserLogin, UserResponse
from app.repositories.crud import create_user, authenticate_user, get_user_by_email
from app.core.security import create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing = get_user_by_email(db, user.email)
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = create_user(db, user.email, user.password)
    return new_user

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    # Accepts JSON body matching UserLogin schema
    auth_user = authenticate_user(db, user.email, user.password)
    if not auth_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"user_id": auth_user.id})
    return {"access_token": token, "token_type": "bearer"}