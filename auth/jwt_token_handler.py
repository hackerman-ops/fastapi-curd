from utils.fastapi_keycloak.keycloak_api_auth import keycloak_openid
from utils.database import DBApi
from migrations.models import Account
from migrations.models import Company
from schemas.base_schema import UserIdentity
from conf.settings import backend_settings
from fastapi import HTTPException, status
from logging import get_logger

logger = get_logger(__name__)


def get_user_info_from_token(token: str) -> UserIdentity:
    """
    Check if token is valid
    return:
        {'acr': '1',
     'active': True,
     'allowed-origins': ['/*'],
     'aud': 'account',
     'azp': 'space_brain',
     'client_id': 'space_brain',
     'email': 'example170039138@example.com',
     'email_verified': True,
     'exp': 1702545783,
     'family_name': 'Example',
     'given_name': 'Example',
     'iat': 1702545483,
     'iss': 'http://localhost/realms/brain',
     'jti': '3ae29917-408a-4fa5-901d-5a0809761ead',
     'name': 'Example Example',
     'preferred_username': 'example170039138@example.com',
     'realm_access': {'roles': ['super_admin',
                                'offline_access',
                                'uma_authorization',
                                'default-roles-space_brain']},
     'resource_access': {'account': {'roles': ['manage-account',
                                               'manage-account-links',
                                               'view-profile']}},
     'scope': 'openid profile email',
     'session_state': 'e8f834c3-285e-4695-8471-5f70939aa478',
     'sid': 'e8f834c3-285e-4695-8471-5f70939aa478',
     'sub': 'ca11f18c-d490-4f42-b34e-950b647bbe5f',
     'typ': 'Bearer',
     'username': 'example170039138@example.com'}
    """

    token_info = keycloak_openid.introspect(token)
    logger.info(f"token_info: {token_info}")
    is_active = token_info.get("active")
    if not is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user status is expired, please try again",
        )
    resource_access = token_info.get("resource_access")
    user_roles = (
        resource_access.get(backend_settings.keycloak_client_id, {})
        if resource_access
        else {}
    )
    # 获取客户端角色
    user_roles = user_roles.get("roles") if user_roles else []
    if not user_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="api is not permitted"
        )
    keycloak_user_id = token_info.get("sub")
    user = DBApi().get_one(
        condition={
            "keycloak_user_code": keycloak_user_id,
            "deleted": False,
            "status": True,
        },
        db_model=Account,
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="account doesn't exsited"
        )
    category = user.category_id
    if category == "company":
        company_id = user.company_id

        company = DBApi().get_one(
            condition={"id": company_id, "deleted": False, "status": True},
            db_model=Company,
        )
        if not company:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="company doesn't exsited",
            )
    return UserIdentity(
        email=token_info.get("email"),
        user_id=user.id,
        keycloak_roles=user_roles,
        user_name=user.name,
        company_name=user.company_name,
        company_id=user.company_id,
    )
