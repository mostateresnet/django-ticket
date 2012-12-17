from django.conf.urls.defaults import *
from issues.views import *


urlpatterns = patterns('',
                       url(r'^$', ProjectListView.as_view(), name="project_list"),
                       url(r'^new_project/$', ProjectNewView.as_view(), name="project_new"),
                       url(r'^profile/(?P<user_id>\d+)$', UserListView.as_view(), name="user_profile_view"),
                       url(r'^(?P<slug>[\w-]+)/$', ProjectDetailView.as_view(), name="project_detail"),
                       url(r'^(?P<slug>[\w-]+)/filter/(?P<filter>\S+)$', ProjectDetailView.as_view(), name="project_detail"),
                       url(r'^(?P<slug>[\w-]+)/(?P<pk>\d+)$', IssueDetailView.as_view(), name="issue_detail"),
                       url(r'^(?P<slug>[\w-]+)/sort$', sort_issue, name="sort_issue"),
                       url(r'^(?P<slug>[\w-]+)/new$', new_issue, name="new_issue"),
                       url(r'^(?P<slug>[\w-]+)/milestone/(?P<pk>[\w-]+)/chart$', BurndownChartView.as_view(), name="burndown_chart"),
                       url(r'^(?P<slug>[\w-]+)/tags/$', TagCreateView.as_view(), name="tag_create_view"),
                       url(r'^(?P<slug>[\w-]+)/tags/(?P<pk>\d+)$', TagUpdateView.as_view(), name="tag_update_view"),
                       )
