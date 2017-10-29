from django.conf.urls import url, include
from aristotle_mdr.contrib.user_management import views, org_backends


urlpatterns = [
    # url(r'^accounts/signup', views.NewUserSignupView.as_view(), name="new_user_signup"),
    url(r'^account/registry/invitations/', include(org_backends.NewUserInvitationBackend().get_urls())),
    url(r'^account/registry/users/$', views.RegistryOwnerUserList.as_view(), name="registry_user_list"),
    url(r'^account/registry/users/deactivate/(?P<user_pk>\d+)/$', views.DeactivateRegistryUser.as_view(), name="deactivate_user"),
    url(r'^account/registry/users/reactivate/(?P<user_pk>\d+)/$', views.ReactivateRegistryUser.as_view(), name="reactivate_user"),
]
