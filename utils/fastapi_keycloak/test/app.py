import random
from typing import List, Optional

import uvicorn
from fastapi import Depends, Query, Body

from pydantic import SecretStr

from utils.fastapi_keycloak import (
    FastAPIKeycloak,
    HTTPMethod,
    KeycloakUser,
    OIDCUser,
    UsernamePassword,
    KeycloakError,
)

idp = FastAPIKeycloak(
    server_url="http://localhost:80",
    client_id="space_brain",
    client_secret="ef73ufiZhOsMK8D5tu3hJSRfrKvKlU8A",
    admin_client_id="admin-cli",
    admin_client_secret="7aRDPRYk1UXJiLVzU960glng8pQFE5FY",
    realm="space_brain",
    callback_uri="http://localhost:8081/callback",
)


# idp.add_swagger_config(app)


def proxy_admin_request(
    relative_path: str,
    method: HTTPMethod,
    additional_headers: dict = Body(None),
    payload: dict = Body(None),
):
    return idp.proxy(
        additional_headers=additional_headers,
        relative_path=relative_path,
        method=method,
        payload=payload,
    )


def get_identity_providers():
    return idp.get_identity_providers()


def get_idp_config():
    return idp.open_id_configuration


# User Management


def get_users():
    return idp.get_all_users()


def get_user_by_query(query: str = None):
    return idp.get_user(query=query)


# 验证OK
def create_user(
    first_name: str,
    last_name: str,
    email: str,
    password: SecretStr,
    initial_roles: List[str] = None,
    user_name: str = None,
    groups: List[str] = None,
):
    return idp.create_user(
        first_name=first_name,
        last_name=last_name,
        username=user_name,
        email=email,
        password=password.get_secret_value(),
        initial_roles=initial_roles,
        groups=groups,
        send_email_verification=False,
    )


def get_user(user_id: str = None):
    return idp.get_user(user_id=user_id)


def update_user(user: KeycloakUser):
    return idp.update_user(user=user)


def change_password(user_id: str, new_password: SecretStr):
    return idp.change_password(user_id=user_id, new_password=new_password)


def send_email_verification(user_id: str):
    return idp.send_email_verification(user_id=user_id)


# Role Management


def get_all_roles():
    return idp.get_all_roles()


def get_role(role_name: str):
    return idp.get_roles([role_name])


def add_role(role_name: str):
    return idp.create_role(role_name=role_name)


def delete_roles(role_name: str):
    return idp.delete_role(role_name=role_name)


# Group Management


# 验证OK
def get_all_groups():
    return idp.get_all_groups()


# 验证OK
def get_group(group_name: str):
    return idp.get_groups([group_name])


# 验证OK
def get_group_by_path(path: str):
    return idp.get_group_by_path(path)


# 验证OK
def add_group(group_name: str, parent_id: Optional[str] = None):
    return idp.create_group(group_name=group_name, parent=parent_id)


def delete_groups(group_id: str):
    return idp.delete_group(group_id=group_id)


# User Roles


def add_roles_to_user(user_id: str, roles: Optional[List[str]] = Query(None)):
    return idp.add_user_roles(user_id=user_id, roles=roles)


def get_user_roles(user_id: str):
    return idp.get_user_roles(user_id=user_id)


def delete_roles_from_user(user_id: str, roles: Optional[List[str]] = Query(None)):
    return idp.remove_user_roles(user_id=user_id, roles=roles)


# User Groups


def add_group_to_user(user_id: str, group_id: str):
    return idp.add_user_group(user_id=user_id, group_id=group_id)


def get_user_groups(user_id: str):
    return idp.get_user_groups(user_id=user_id)


def delete_groups_from_user(user_id: str, group_id: str):
    return idp.remove_user_group(user_id=user_id, group_id=group_id)


# Example User Requests


def protected(user: OIDCUser = Depends(idp.get_current_user())):
    return user


def get_current_users_roles(user: OIDCUser = Depends(idp.get_current_user())):
    return user.roles


def company_admin(
    user: OIDCUser = Depends(idp.get_current_user(required_roles=["admin"])),
):
    return f"Hi admin {user}"


def login(user: UsernamePassword = Body(...)):
    return idp.user_login(
        username=user.username, password=user.password.get_secret_value()
    )


# Auth Flow


def login_redirect():
    return idp.login_uri


def callback(session_state: str, code: str):
    return idp.exchange_authorization_code(session_state=session_state, code=code)


def logout():
    return idp.logout_uri


if __name__ == "__main__":
    import pprint

    f = random.randint(1, 999999999)
    # result = add_group(f"公司{f}")
    # result = get_group("公司A")
    # result = get_all_groups()
    # result = get_all_roles()
    # pprint.pprint(result)
    # delete_roles(role_name="super_admin")
    # role_r = add_role("super_admin")
    #
    #
    # create_user(first_name="super", last_name="admin",
    #             user_name=f"吴国ss{f}s2斌",
    #             password=SecretStr("dcs12sds3456"),
    #             initial_roles=["super_admin"],
    #             email=f"2359717efw{f}s5@qq.com", groups=["公司1"])
    # get_user(user_id="118eceb9-dc77-41d8-b1d5-fb3a5664ab10")
    # g = login(user=UsernamePassword(username="吴国ss201220908s2斌",
    #                                 password=SecretStr("dcs12sds3456")))
    # access_token = g.access_token
    user = idp.token_is_valid(token=idp.admin_token)
    pprint.pprint(user)
    pprint.pprint(get_role("super_admin"))
