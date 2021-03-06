# pylint: disable-msg=E1120
try:
    from django.conf.urls import patterns, url
except ImportError:
    from django.conf.urls.defaults import patterns, url

from issues.views import (ProjectListView, ProjectNewView, ProjectSortView,
                          UserListView, UserSortIssueView, ProjectDetailView, IssueDetailView,
                          BurndownChartView, TagCreateView, TagUpdateView, CommitCreateView,
                          NoteCreateView, TagSearchView, sort_issue, new_issue)


urlpatterns = patterns('',
                       url(r'^$', ProjectListView.as_view(), name="project_list"),
                       url(r'^tags/$', TagCreateView.as_view(), name="tag_create_view"),
                       url(r'^tags/(?P<pk>\d+)$', TagUpdateView.as_view(), name="tag_update_view"),
                       url(r'^tags/search$', TagSearchView.as_view(), name="tag_search_view"),
                       url(r'^new_project/$', ProjectNewView.as_view(), name="project_new"),
                       url(r'^project_sort/$', ProjectSortView.as_view(), name="project_sort"),
                       url(r'^profile/(?P<user_id>\d+)$', UserListView.as_view(), name="user_profile_view"),
                       url(r'^profile/(?P<user_id>\d+)/sort$', UserSortIssueView.as_view(), name="user_sort_issue_view"),
                       url(r'^(?P<slug>[\w-]+)/$', ProjectDetailView.as_view(), name="project_detail"),
                       url(r'^(?P<slug>[\w-]+)/filter/(?P<filter>\S+)$', ProjectDetailView.as_view(), name="project_detail"),
                       url(r'^issue/(?P<pk>\d+)$', IssueDetailView.as_view(), name="issue_detail"),
                       url(r'^(?P<slug>[\w-]+)/sort$', sort_issue, name="sort_issue"),
                       url(r'^(?P<slug>[\w-]+)/new$', new_issue, name="new_issue"),
                       url(r'^(?P<slug>[\w-]+)/milestone/(?P<pk>[\w-]+)/chart$', BurndownChartView.as_view(), name="burndown_chart"),
                       url(r'^(?P<pk>\d+)/createcommit/$', CommitCreateView.as_view(), name="commit_create_view"),
                       url(r'^(?P<pk>\d+)/createnote/$', NoteCreateView.as_view(), name="note_create_view"),
                       )
