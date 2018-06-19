from rest_framework.authtoken.models import Token
from django.db import models
from django.conf import settings
from jsonfield import JSONField

from django.utils.translation import ugettext_lazy as _

class AristotleToken(Token):

    name = models.CharField(
        max_length=100,
        default='Token'
    )
    key = models.CharField(_("Key"), max_length=40, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='auth_token',
        on_delete=models.CASCADE,
        verbose_name=_("User")
    )
    permissions = JSONField()

    def __str__(self):
        return self.name
