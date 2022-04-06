# GOOGLE OIDC
# CONFIG: https://accounts.google.com/.well-known/openid-configuration

# https://developers.google.com/identity/protocols/oauth2/web-server#example
GOOGLE_CLIENT_SECRETS_FILE = "path/to/client_secret.json" # or env("GOOGLE_CLIENT_SECRETS_FILE")
GOOGLE_OAUTH_SCOPES = [
    # https://developers.google.com/identity/protocols/oauth2/scopes#google-sign-in
    "openid",
    # https://developers.google.com/identity/protocols/oauth2/scopes#oauth2
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]
