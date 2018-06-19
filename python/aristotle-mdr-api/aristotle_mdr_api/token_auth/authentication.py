from rest_framework.authentication import TokenAuthentication
from aristotle_mdr_api.token_auth.models import AristotleToken

class AristotleTokenAuthentication(TokenAuthentication):
    model = AristotleToken
