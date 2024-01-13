from keycloak import KeycloakOpenID
import pprint

# Configure client
keycloak_openid = KeycloakOpenID(
    server_url="http://localhost:80/",
    client_id="space_brain",
    realm_name="space_brain",
    client_secret_key="ef73ufiZhOsMK8D5tu3hJSRfrKvKlU8A",
)

# Get WellKnown
config_well_known = keycloak_openid.well_known()
# pprint.pprint(config_well_known)

token = keycloak_openid.token("user01", "example")
pprint.pprint(token)

# f = keycloak_openid.decode_token(token['access_token'])
# Introspect Token
token_info = keycloak_openid.introspect(
    "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJPY1JUMVlqMnpKNTU2R2J6M0dtZmRjOGJGb0ZWdHpWak5FaUNhWW9yTHF3In0"
)
pprint.pprint(token_info)

# Decode Token
