from rest_framework.authtoken.models import Token
from jsonfield import JSONField

class AristotleToken(Token):

    permissions = JSONField()
