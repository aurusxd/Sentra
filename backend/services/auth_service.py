
from fastapi import HTTPException, status

from backend.core.password import verify_password
from backend.core.jwt import create_access_token
from backend.services.user_service import UserService

class AuthService:
    def __init__(self):
        self.service = UserService()

    async def login(self,name:str,password:str):
        user = await self.service.get_by_name(name)
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect name or password",
            )
        
        is_verify = verify_password(password,user.password_hash)
        if not is_verify:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Incorrect name or password",
                )
        token = create_access_token(user_id=user.id)

        return {"access_token": token} 
