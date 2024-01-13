import os
import traceback
from typing import Optional

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from auth.jwt_token_handler import get_user_info_from_token
from conf.base_model import UserIdentity


class AuthBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(
        self,
        request: Request,
    ):
        credentials: Optional[HTTPAuthorizationCredentials] = await super().__call__(
            request
        )
        self.check_scheme(credentials)
        token = credentials.credentials  # pyright: ignore reportPrivateUsage=none
        return await self.authenticate(
            token,
        )

    def check_scheme(self, credentials):
        if credentials and credentials.scheme != "Bearer":
            raise HTTPException(status_code=401, detail="Token must be Bearer")
        elif not credentials:
            raise HTTPException(
                status_code=403, detail="Authentication credentials missing"
            )

    async def authenticate(
        self,
        token: str,
    ) -> UserIdentity:
        if os.environ.get("AUTHENTICATE") == "false":
            return self.get_test_user()
        try:
            user = get_user_info_from_token(token)
            return user
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            traceback.print_exc()
            raise HTTPException(status_code=401, detail="Invalid token")

    @staticmethod
    def get_test_user() -> UserIdentity:
        return UserIdentity(
            email="235717455@qq.com",
            user_id=1,
            keycloak_roles=["super_admin"],
            user_name="test",
            company_name="测试",
            company_id=1,
        )


def get_current_user(user: UserIdentity = Depends(AuthBearer())) -> UserIdentity:
    return user
