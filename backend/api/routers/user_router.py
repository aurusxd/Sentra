from fastapi import APIRouter, HTTPException, status

from backend.core.jwt import create_access_token
from backend.schemas.user_schema import UserCreate, UserLogin, Token
from backend.services.auth_service import AuthService
from backend.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["Auth"])

auth_service = AuthService()
user_service = UserService()

@router.post("/login", response_model=Token)
async def login(data: UserLogin):
    return await auth_service.login(
        name=data.name,
        password=data.password,
    )

@router.post("/register", response_model=Token)
async def register(data: UserCreate):
        # existing_user = await user_service.get_by_name(data.name)

        # if existing_user is not None:
        #     raise HTTPException(
        #         status_code=status.HTTP_409_CONFLICT,
        #         detail="User with this name already exists",
        #     )

        user = await user_service.create(data=data)

        token = create_access_token(user_id=user.id)

        return {
            "access_token": token,
            "token_type": "Bearer",
        }