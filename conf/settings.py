from pydantic_settings import BaseSettings

from enum import Enum


class RoleEnum(str, Enum):
    # 公司超级管理员
    SuperAdmin = "super_admin"
    # 管理员
    Manager = "manager"
    # 员工
    User = "user"
    # 运营
    Operator = "operator"


class BackendSettings(BaseSettings):
    """
    API settings
    """

    service_domain: str

    user_storage_max_size: int = 524288000
    user_single_file_storage_max_size: int = 52428800
    common_file_bucket_name: str = "user_files"
    expiry_duration: int = 2 * 60 * 60

    max_brain_size: int = 52428800
    max_brain_per_user: int = 5

    # redis
    redis_host: str
    redis_port: int = 6379
    redis_user_name: str
    redis_passwd: str
    # postgres
    POSTGRES_DB_URL: str = (
        "postgresql+psycopg2://postgres:postgres@127.0.0.1:5432/my_database"
    )

    # keycloak
    keycloak_domain: str
    keycloak_realm: str
    keycloak_client_id: str
    keycloak_client_secret: str
    keycloak_admin_client_id: str
    keycloak_admin_client_secret: str
    keycloak_auth_url: str

    aes_key: str

    default_avatar_link: str
    user_single_avatar_storage_max_size: int = 32768000
    common_avatar_bucket_name: str = "user_avatar"
    common_avatar_name: str = "common_avatar.ico"
    avatar_expiry_duration: int = 30 * 24 * 60 * 60

    super_admin_role: str = "super_admin"

    celery_broker_url: str

    azure_storage_url: str
    azure_storage_connect_string: str
    azure_storage_key: str


backend_settings = BackendSettings()

# for key, value in BackendSettings.__annotations__.items():
#     print(f"{key.upper()}=")
