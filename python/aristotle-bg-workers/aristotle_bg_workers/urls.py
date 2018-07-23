from django.conf.urls import url
from aristotle_bg_workers import views

urlpatterns = [
    url(r'^tasks/dbstatus', views.GetTaskStatusView.as_view(), name="dbstatus"),
    url(r'^account/tasks/$', views.TaskRunnerView.as_view(), name="run_task"),
    url(r'^account/tasks/history/$', views.TaskListView.as_view(), name="task_history"),
    url(r'^account/tasks/recent/$', views.TaskListLimitedView.as_view(), name="task_history_recent"),
    url(r'^tasks/starttask/(?P<task_name>\w+)', views.GenericTaskView.as_view(), name="starttask")
]
