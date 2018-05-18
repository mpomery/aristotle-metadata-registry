from rest_framework.authtoken.models import Token
from django.db.models.fields import CharField
from jsonfield import JSONField

class AristotleToken(Token):

    name = CharField(
        max_length=100,
        default='Token'
    )
    permissions = JSONField()
