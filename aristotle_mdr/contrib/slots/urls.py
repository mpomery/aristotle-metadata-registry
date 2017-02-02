from django.conf.urls import url
from aristotle_mdr.contrib.slots import views


urlpatterns = [
    url(r'^slot/(?P<slot_type_id>\d+)/?$', views.SimilarSlotsView.as_view(), name='similar_slots'),
]
