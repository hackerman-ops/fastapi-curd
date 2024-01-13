# KEYCLOAK ADMIN
#
# 创建realm
# 创建client
# client关联scope
# 创建角色
# admin-cli service account role 关联角色

import json
import pprint
import random

from utils.fastapi_keycloak.keycloak_api_auth import keycloak_admin
from conf.settings import backend_settings

f3 = random.randint(1, 384357845)

# Add user
# new_user = keycloak_admin.create_user({"email": f"example{f3}@example.com",
#                                        "username": "user01",
#                                        "enabled": True,
#                                        "emailVerified": True,
#                                        "firstName": "user01",
#                                        "groups": ["PA"],
#
#                                        "lastName": "user01", "credentials": [
#         {"value": "example", "type": "password"}]}, exist_ok=False)
# pprint.pprint(new_user)
# role = keycloak_admin.get_realm_role("user")
# keycloak_admin.assign_realm_roles(user_id=new_user, roles=[role])

# client_role = keycloak_admin.get_client_role(
#     client_id="a61a7c29-0759-4f5f-9d72-65f4d638eb06", role_name="user")
# keycloak_admin.assign_client_role(
#     client_id="a61a7c29-0759-4f5f-9d72-65f4d638eb06",
#     user_id="7be87023-6bc2-4680-a673-b118d2729d79",
#     roles=[client_role])
# Get all roles for the realm or client

#
# # Get all roles for the realm or client that their names includes the searched text
# realm_roles = keycloak_admin.get_realm_roles(search_text="super_admin")
#
# print(realm_roles)
# group = keycloak_admin.create_group({"name": "Example Group"})

# # print(group)
client = keycloak_admin.get_clients()
pprint.pprint(client)
#
client = keycloak_admin.get_client_id(client_id=backend_settings.keycloak_client_id)
print(keycloak_admin.get_client_roles(client_id=client))
pprint.pprint(client)
# print("=====打印权限=====")
# permission = keycloak_admin.get_client_authz_permissions(
#     client_id="a61a7c29-0759-4f5f-9d72-65f4d638eb06")
# pprint.pprint(permission)
#
# policy = keycloak_admin.get_client_authz_policies(
#     client_id="a61a7c29-0759-4f5f-9d72-65f4d638eb06")
# print("=====打印策略=====")
# pprint.pprint(policy)
#
# resource = keycloak_admin.get_client_authz_resources(
#     client_id="a61a7c29-0759-4f5f-9d72-65f4d638eb06")
# print("=====打印资源=====")
# pprint.pprint(resource)
# client = keycloak_admin.get_client(
#     client_id="a61a7c29-0759-4f5f-9d72-65f4d638eb06")

# ath = keycloak_admin.get_client_authz_settings(
#     client_id="a61a7c29-0759-4f5f-9d72-65f4d638eb06")
# pprint.pprint(ath)
# with open("./client_authz_settings.json", "w") as f:
#     f.write(json.dumps(ath))
#
# # 获取authjson
# ath = keycloak_admin.get_client_authz_settings(
#     client_id="a61a7c29-0759-4f5f-9d72-65f4d638eb06")
