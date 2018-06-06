django-admin migrate
# django-admin createcachetable
gunicorn -b 0.0.0.0:8000 -w 2 wsgi:application
