from django.conf.urls.defaults import *
from issues.views import *


urlpatterns = patterns('',
    url(r'^$', ProjectListView.as_view(), name="project_list"),
    url(r'^(?P<slug>[\w-]+)/$', ProjectDetailView.as_view(), name="project_detail"),
    url(r'^(?P<slug>[\w-]+)/closed/$', ProjectDetailViewClosed.as_view(), name="project_detail_closed"),
    url(r'^(?P<slug>[\w-]+)/(?P<pk>\d+)$', IssueDetailView.as_view(), name="issue_detail"),
    url(r'^(?P<slug>[\w-]+)/sort$', sort_issue, name="sort_issue"),
    url(r'^(?P<slug>[\w-]+)/new$', new_issue, name="new_issue"),
    url(r'^(?P<slug>[\w-]+)/milestone/(?P<pk>[\w-]+)/chart$', BurndownChartView.as_view(), name="burndown_chart"),
)
