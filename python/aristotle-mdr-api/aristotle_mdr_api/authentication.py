from rest_framework.authentication import TokenAuthentication
from aristotle_mdr_api.models import AristotleToken

class AristotleTokenAuthentication(TokenAuthentication):
    model = AristotleToken
