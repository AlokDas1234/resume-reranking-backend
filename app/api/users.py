from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.auth.security import hash_password

# from app.schemas.auth import LoginRequest, Token
from app.auth.security import verify_password, create_access_token
from app.auth.security import get_current_user
from app.schemas.auth import Token
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException, Response
router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if username already exists


    existing_username = db.query(User).filter(
        User.username == user.username
    ).first()

    if existing_username:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    existing_email = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    # Create new user
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user



@router.post("/login")
def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = (
        db.query(User)
        .filter(User.username == form_data.username)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    if not verify_password(
        form_data.password,
        user.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    token = create_access_token(
        {
            "sub": str(user.id)
        }
    )

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,      # True when using HTTPS in production
        samesite="lax"
    )

    # return {
    #     "access_token": token,
    #     "token_type": "bearer"
    # }
    return {
        "message": "Login successful"
    }


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(
        key="access_token"
    )

    return {
        "message": "Logout successful"
    }
@router.get("/me")
def get_profile(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email
    }
# @router.get("/me")
# def get_profile(current_user: str = Depends(get_current_user)):
#     return {
#         "message": f"Welcome {current_user.username}",
#         "user_id": current_user.id,
#         "email": current_user.email
#     }


# @router.post("/login", response_model=Token)
# def login(
#     form_data: OAuth2PasswordRequestForm = Depends(),
#     db: Session = Depends(get_db)
# ):
#
#     user = (
#         db.query(User)
#         .filter(User.username == form_data.username)
#         .first()
#     )
#
#     if not user:
#         raise HTTPException(
#             status_code=401,
#             detail="Invalid username or password"
#         )
#
#     if not verify_password(
#         form_data.password,
#         user.hashed_password
#     ):
#         raise HTTPException(
#             status_code=401,
#             detail="Invalid username or password"
#         )
#
#     token = create_access_token(
#         {
#             "sub": str(user.id)
#         }
#     )
#
#     return {
#         "access_token": token,
#         "token_type": "bearer"
#     }


# @router.post("/login", response_model=Token)
