from fastapi import APIRouter, Depends, HTTPException, Response, status

from backend.config import COOKIE_SECURE, REGISTRATION_ADMIN_EMAIL
from backend.core.security import get_current_user
from backend.database.models.user import User
from backend.schemas.user_schema import UserCreate, UserLogin, UserRead, UserSession
from backend.services.auth_service import AuthService
from backend.services.user_service import UserService
from backend.utils.rate_limit import rate_limit

router = APIRouter(prefix="/auth", tags=["Auth"])

auth_service = AuthService()
user_service = UserService()

@router.post("/login", dependencies=[Depends(rate_limit("login", 10, 300))])
async def login(data: UserLogin, response: Response):
    result = await auth_service.login(
        name=data.name,
        password=data.password,
    )
    response.set_cookie(
        key="access_token",
        value=result["access_token"],
        max_age=60 * 60 * 24,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="none" if COOKIE_SECURE else "lax",
        path="/",
    )
    return {"ok": True}

@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(rate_limit("register", 10, 3600))])
async def register(data: UserCreate, current_user: User = Depends(get_current_user)):
    if not REGISTRATION_ADMIN_EMAIL or current_user.email.lower() != REGISTRATION_ADMIN_EMAIL.lower():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the registration administrator can create accounts")
    return await user_service.create(data=data)


@router.get("/me", response_model=UserSession)
async def me(current_user: User = Depends(get_current_user)):
    return UserSession(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        created_at=current_user.created_at,
        can_register_users=bool(
            REGISTRATION_ADMIN_EMAIL
            and current_user.email.lower() == REGISTRATION_ADMIN_EMAIL.lower()
        ),
    )


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token", path="/")
    return {"ok": True}
