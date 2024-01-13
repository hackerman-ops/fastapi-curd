import ast
import json
from utils.storage.redis_cache import cache
from utils.fastapi_keycloak.keycloak_api_auth import keycloak_admin
from conf.settings import backend_settings
from logger import get_logger

logger = get_logger(__name__)


def load_config():
    client_name = backend_settings.keycloak_admin_client_id
    client_id = keycloak_admin.get_client_id(client_id=client_name)
    data = keycloak_admin.get_client_authz_settings(client_id=client_id)
    policies_roles = {}
    policies_resource = {}
    role_resources = {}
    for pol in data["policies"]:
        if pol["type"] == "role":
            policies_roles[pol["name"]] = [
                role["id"] for role in json.loads(pol["config"]["roles"])
            ]
        if pol["type"] == "resource":
            resources = ast.literal_eval(pol["config"].get("resources", "[]"))

            policies_list = ast.literal_eval(pol["config"]["applyPolicies"])

            for pol in policies_list:
                policies_resource[pol] = resources
    for pol, roles in policies_roles.items():
        for role in roles:
            role = role.split("/")[1]
            role_resources.setdefault(role, []).extend(policies_resource[pol])
    logger.info(f"role_resources: {role_resources}")
    cache.set(
        "app_role_resources", json.dumps(role_resources, ensure_ascii=False), ex=5 * 60
    )


if __name__ == "__main__":
    load_config()
