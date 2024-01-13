from typing import List, Optional, Union

from fastapi import Depends, HTTPException, status

from auth.auth_bearer import get_current_user
from src.account.models import UserIdentity
from src.types import RoleEnum


def has_authorization(required_roles: Optional[Union[RoleEnum, List[RoleEnum]]] = None):
    """
    Decorator to check if the user has the required role(s) for the api
    param: required_roles: The role(s) required to access the brain
    return: A wrapper function that checks the authorization
    """

    async def wrapper(current_user: UserIdentity = Depends(get_current_user)):
        nonlocal required_roles
        if isinstance(required_roles, str):
            required_roles = [required_roles]
        if current_user.role_en not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="无权访问此接口"
            )

    return wrapper
