# from fastapi import APIRouter, Depends
# from sqlalchemy.orm import Session
# from app.database import get_db
# from app.schemas.auth_schema import UserRegister, UserLogin, TokenResponse, UserResponse
# from app.services.auth_service import register_user, login_user
# from app.core.dependencies import get_current_user
# from app.models.user import User


# router = APIRouter(prefix="/api/auth", tags=["Auth"])


# @router.post("/register", response_model=UserResponse)
# def register(payload: UserRegister, db: Session = Depends(get_db)):
#     user = register_user(db, payload.email, payload.password)
#     return user


# @router.post("/login", response_model=TokenResponse)
# def login(payload: UserLogin, db: Session = Depends(get_db)):
#     token = login_user(db, payload.email, payload.password)
#     return {
#         "access_token": token,
#         "token_type": "bearer"
#     }


# @router.get("/me", response_model=UserResponse)
# def get_me(current_user: User = Depends(get_current_user)):
#     return current_user

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth_schema import UserRegister, UserLogin, TokenResponse, UserResponse
from app.services.auth_service import register_user, login_user
from app.core.dependencies import get_current_user
from app.models.user import User


router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    user = register_user(db, payload.email, payload.password)
    return user


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    token = login_user(db, payload.email, payload.password)
    return {
        "access_token": token,
        "token_type": "bearer"
    }


@router.post("/token", response_model=TokenResponse)
def swagger_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    token = login_user(db, form_data.username, form_data.password)
    return {
        "access_token": token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user