REQUIRED_APPS = (
    'aristotle_mdr_api',
    'aristotle_mdr_api.token_auth',
    'rest_framework',
    'rest_framework_swagger',
    'django_filters',
    'django_jsonforms'
)

SERIALIZATION_MODULES = { 'mdrjson' : 'aristotle_mdr_api.serializers.idjson' }

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'aristotle_mdr_api.token_auth.permissions.AristotlePermissions',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'aristotle_mdr_api.token_auth.authentication.AristotleTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    # 'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.NamespaceVersioning'
}
