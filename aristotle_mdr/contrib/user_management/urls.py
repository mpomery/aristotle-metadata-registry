from django.conf.urls import url, include
from aristotle_mdr.contrib.user_management import views


urlpatterns = [
    url(r'^accounts/signup', views.NewUserSignupView.as_view(), name="new_user_signup"),
    url(r'^accounts/registry/invitations/', include(invitation_backend().get_urls())),
]
