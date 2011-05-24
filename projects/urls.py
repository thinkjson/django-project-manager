from django.conf.urls.defaults import *

urlpatterns = patterns('projects.views',
    (r'^$', 'projects_overview'),
    (r'^add/$', 'add_project'),
    (r'^edit/(?P<project_id>\d{1,6})/$', 'add_project'),
    (r'^delete/(?P<project_id>\d{1,6})/$', 'delete_project'),
    (r'^project/(?P<project_id>\d{1,6})/$', 'show_project'),
    (r'^task/(?P<project_id>\d{1,6})/$', 'edit_task'),
    (r'^task/(?P<project_id>\d{1,6})/(?P<task_id>\d{1,6})/$', 'edit_task'),
)