from django.conf.urls import url
from aristotle_mdr_api.token_auth import views

urlpatterns = [
    url(r'^list/', views.TokenListView.as_view(), name='token_list'),
    url(r'^create/', views.TokenCreateView.as_view(), name='token_create'),
    url(r'^update/(?P<token_id>\d+)/', views.TokenUpdateView.as_view(), name='token_update'),
    url(r'^delete/(?P<token_id>\d+)/', views.TokenDeleteView.as_view(), name='token_delete'),
    url(r'^regenerate/(?P<token_id>\d+)/', views.TokenRegenerateView.as_view(), name='token_regenerate'),
]
