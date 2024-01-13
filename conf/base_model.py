from typing import Any, Optional, Union

from pydantic import BaseModel


class ResponseStruct(BaseModel):
    data: Any = None
    message: str = "Done"
    type: str = "success"
    code: int = 200


class NoDataResponseStruct(ResponseStruct):
    data: None
    message: str = "Done"
    type: str = "success"


class ResponseStatusTypeCode(BaseModel):
    success: int = "success"
    failed: int = "failed"


class UserIdentity(BaseModel):
    email: Optional[str]
    user_id: int
    keycloak_roles: list
    user_name: str
    company_name: str
    company_id: int

