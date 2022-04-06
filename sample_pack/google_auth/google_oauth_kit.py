from google.auth.transport.requests import Request
from google.oauth2.id_token import verify_oauth2_token
from google_auth_oauthlib.flow import Flow
from . import settings


def generate_google_auth_redirection(redirect_url):
    # https://developers.google.com/identity/protocols/oauth2/web-server#example
    # google example is for flask, and this function is equivalent of
    # authorize function in doc
    flow = Flow.from_client_secrets_file(
        settings.GOOGLE_CLIENT_SECRETS_FILE, scopes=settings.GOOGLE_OAUTH_SCOPES
    )
    flow.redirect_uri = redirect_url
    authorization_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
    )

    return authorization_url


def get_google_oauth_data(redirect_url, code):
    # https://developers.google.com/identity/protocols/oauth2/web-server#example
    # equivalent of oauth2callback function

    flow = Flow.from_client_secrets_file(
        settings.GOOGLE_CLIENT_SECRETS_FILE, scopes=settings.GOOGLE_OAUTH_SCOPES
    )

    flow.redirect_uri = redirect_url
    flow.fetch_token(code=code)
    credentials = flow.credentials
    id_token = verify_oauth2_token(
        credentials.id_token, Request(), credentials.client_id
    )

    return {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
        "id_token": id_token,
    }
