from django.conf.urls import url
from aristotle_mdr.contrib.user_management import views


urlpatterns = [
    url(r'^/accounts/signup', views.NewUserSignupView.as_view(), name="new_user_signup"),
]
