from keycloak import KeycloakOpenID
from keycloak import KeycloakAdmin
from keycloak import KeycloakOpenIDConnection
from conf.settings import backend_settings

keycloak_openid = KeycloakOpenID(
    server_url=backend_settings.keycloak_domain,
    client_id=backend_settings.keycloak_admin_client_id,
    realm_name=backend_settings.keycloak_realm,
    client_secret_key=backend_settings.keycloak_admin_client_secret,
)

keycloak_connection = KeycloakOpenIDConnection(
    server_url=backend_settings.keycloak_domain,
    client_id=backend_settings.keycloak_admin_client_id,
    realm_name=backend_settings.keycloak_realm,
    user_realm_name=backend_settings.keycloak_realm,
    client_secret_key=backend_settings.keycloak_admin_client_secret,
    verify=True,
)

keycloak_admin = KeycloakAdmin(connection=keycloak_connection)
