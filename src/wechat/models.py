from typing import Optional, Union

from pydantic import BaseModel

from common.model import ResponseStruct
from sql_model.models import ManageAccount
from sql_model.models import ManageAccountRole
from sql_model.models import Store
from utils.pydantic_sqlalchemy import sqlalchemy_model_update_to_pydantic
from utils.pydantic_sqlalchemy import sqlalchemy_to_pydantic


class UserIdentity(BaseModel):
    email: Optional[str]
    user_id: int
    user_name: str
    role_en: str
    store_id: Union[int, None]
    store_name: Union[str, None]


class NewUserPlatformAuthModel(BaseModel):

    platform: str
    manage_account_id: int
    open_id: str
    app_id: str


class NewUserRequestModel(BaseModel):
    name_cn: Optional[str]
    email: Optional[str] = None
    password: str
    phone_number: str
    is_active: bool = 1
    immediate_superior_id: int
    introduction: Optional[str] = None


class NewUserModel(NewUserRequestModel):
    name_en: Optional[str]
    name_num_tag: Optional[int]
    login_name_en: Optional[str]


class UserLoginRequestModel(BaseModel):

    employee_number: str
    password: str


class WechatMiniLoginModel(BaseModel):

    code: str


class WechatLoginModel(BaseModel):

    code: str
    scene_code: str


class LoginResponseModel(BaseModel):
    email: str = None
    user_id: int = None
    user_name: str = None
    role_en: Optional[str]
    token: str = Optional[str]
    store_id: Optional[int]
    store_name: Optional[str]


StoreModel = sqlalchemy_to_pydantic(Store)

CreateStoreModel = sqlalchemy_to_pydantic(
    Store, exclude=["id", "t_created", "t_modified"]
)

ManageAccountRoleModel = sqlalchemy_to_pydantic(ManageAccountRole)

CreateManageAccountRoleModel = sqlalchemy_to_pydantic(
    ManageAccountRole, exclude=["id", "t_created", "t_modified"]
)

ManageAccountModel = sqlalchemy_to_pydantic(ManageAccount, exclude=["password"])

CreateManageAccountModel = sqlalchemy_to_pydantic(
    ManageAccount,
    exclude=["id", "t_created", "t_modified", "password"],
)

UpdateManageAccountModel = sqlalchemy_model_update_to_pydantic(
    ManageAccount,
    exclude=[
        "id",
        "t_created",
        "t_modified",
        "password"
    ],
)


UpdateStewardManageAccountModel = sqlalchemy_to_pydantic(
    ManageAccount,
    exclude=[
        "id",
        "t_created",
        "t_modified",
        "employee_number",
        "password",
        "phone_number",
        "is_active",
        "immediate_superior_id",
        "immediate_superior_name",
        "store_id",
        "store_name",
        "region_id",
        "region_name",
        "community_id",
        "community_name",
        "name_cn",
        "role_name_en",
        "role_id",
        "role_name_cn",
    ],
)

ManageAccountStewardModel = sqlalchemy_to_pydantic(
    ManageAccount,
    exclude=[
        "t_created",
        "t_modified",
        "employee_number",
        "password",
        "phone_number",
        "is_active",
        "immediate_superior_id",
        "immediate_superior_name",
        "store_id",
        "store_name",
        "region_id",
        "region_name",
        "community_id",
        "community_name",
        "name_cn",
        "role_name_en",
        "role_id",
        "role_name_cn",
    ],
)

ManageAccountModelToken = sqlalchemy_to_pydantic(ManageAccount, exclude=["password","t_created", "t_modified"])

class Token(BaseModel):
    user_info: ManageAccountModelToken = None
    token: str = None


class LoginResponse(ResponseStruct):
    data: Token = None


class ModifyUserInfoModel(BaseModel):
    old_password: str
    new_password: str
    confirming_password: str



NoAuthManageAccountStewardModel = sqlalchemy_to_pydantic(
    ManageAccount,
    exclude=[
        "t_created",
        "t_modified",
        "employee_number",
        "password",
    ],
)