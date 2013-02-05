"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".
"""

import json
import datetime
from django.test import TestCase
from django.test.utils import override_settings
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from issues.models import Project, Issue, Tag, Note, Commit, Milestone


class ProjectListViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
        self.user2 = User.objects.create_user('jake', 'jakelennon@thebeatles.com', 'jakepassword')

        self.project1 = Project.objects.create(name="project1", slug="project1", status="AC", priority=-1)

        self.issue1 = self.project1.issue_set.create(title="issue1", creator=self.user, assigned_to=self.user, status="AS")
        self.issue2 = self.project1.issue_set.create(title="issue2", creator=self.user2, assigned_to=self.user, status="UA")
        self.issue3 = self.project1.issue_set.create(title="issue3", creator=self.user2, assigned_to=self.user, status="IP")
        self.issue4 = self.project1.issue_set.create(title="issue4", creator=self.user2, assigned_to=self.user, status="CP")
        self.issue5 = self.project1.issue_set.create(title="issue5", creator=self.user, status="UA")

    def test_project_list_responds_200(self):
        """
        Tests that the ProjectListView responds with 200 OK.
        """
        response = self.client.get(reverse('project_list'))
        self.assertEqual(response.status_code, 200, "ProjectListView should respond with HTTP 200 OK")


class UserListViewTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
        self.user2 = User.objects.create_user('jake', 'jakelennon@thebeatles.com', 'jakepassword')

        self.project1 = Project.objects.create(name="project1", slug="project1", status="AC", priority=-1)
        self.issue1 = self.project1.issue_set.create(title="issue1", creator=self.user1, assigned_to=self.user1, status="CP")

    def test_user_list_responds_200(self):
        # user_profile with completed issues
        response = self.client.get(reverse('user_profile_view', args=(str(self.user1.pk), )))
        self.assertEqual(response.status_code, 200, "UserListView should respond with HTTP 200 OK")
        # user_profile without completed issues
        response = self.client.get(reverse('user_profile_view', args=(str(self.user2.pk), )))
        self.assertEqual(response.status_code, 200, "UserListView should respond with HTTP 200 OK")


class ProjectNewViewTest(TestCase):
    def test_project_new_responds_200(self):
        url = '/new_project/'
        response = self.client.post(url, {'name': 'New Project name', 'slug': 'new-project-slug', 'status': 'AC', 'priority': -1})
        project_count = Project.objects.filter(name="New Project name").count()
        self.assertEqual(project_count, 1, "Project did not get inserted successfully")
        self.assertEqual(response.status_code, 200, "ProjectNewView should respond with HTTP 200 OK")

    def test_project_new_form_invalid(self):
        url = '/new_project/'
        response = self.client.post(url, {'name': 'New Project name', 'status': 'AC', 'priority': -1})
        response_data = json.JSONDecoder().decode(response.content)  # parses json string into a python dict
        self.assertEqual(response_data['status'], 'error', "HttpResponse should return an error for this test case")
        self.assertEqual(response.status_code, 200, "ProjectNewView should respond with HTTP 200 OK")


class ProjectSortViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')

        self.project1 = Project.objects.create(name="project1", slug="project1", status="AC", priority=-1)
        self.project2 = Project.objects.create(name="project2", slug="project2", status="AC", priority=-1)
        self.project3 = Project.objects.create(name="project3", slug="project3", status="AC", priority=-1)

    def test_project_sort_view(self):
        url = '/project_sort/'
        project_list = [self.project3.pk, self.project2.pk, self.project1.pk]
        response = self.client.post(url, {'sorted_ids[]': project_list})
        self.project3 = Project.objects.filter(pk=self.project3.pk)[0]
        self.assertEqual(self.project3.priority, 3, "Projects did not sort properly")
        self.assertEqual(response.status_code, 200, "ProjectSortView should respond with HTTP 200 OK")


class UserSortViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')

        self.project1 = Project.objects.create(name="project1", slug="project1", status="AC", priority=-1)

        self.issue1 = self.project1.issue_set.create(title="issue1", creator=self.user, assigned_to=self.user, status="AS")
        self.issue2 = self.project1.issue_set.create(title="issue2", creator=self.user, assigned_to=self.user, status="AS")
        self.issue3 = self.project1.issue_set.create(title="issue3", creator=self.user, assigned_to=self.user, status="AS")

    def test_issue_sorting(self):
        url = reverse('user_sort_issue_view', args=(str(self.user.pk), ))
        issue_list = [self.issue1.pk, self.issue2.pk, self.issue3.pk]
        response = self.client.post(url, {'sorted_ids[]': issue_list})
        self.issue3 = Issue.objects.filter(pk=self.issue3.pk)[0]
        self.assertEqual(self.issue3.user_priority, 1, "Issues did not sort properly")
        self.assertEqual(response.status_code, 200, "UserSortIssueView should respond with HTTP 200 OK")


class ProjectDetailViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
        self.user2 = User.objects.create_user('jake', 'jakelennon@thebeatles.com', 'jakepassword')

        self.project1 = Project.objects.create(name="project1", slug="project1", status="AC", priority=-1)

        self.issue1 = self.project1.issue_set.create(title="issue1", creator=self.user, assigned_to=self.user, status="AS")
        self.issue2 = self.project1.issue_set.create(title="issue2", creator=self.user2, assigned_to=self.user, status="UA")
        self.issue3 = self.project1.issue_set.create(title="issue3", creator=self.user2, assigned_to=self.user, status="IP")
        self.issue4 = self.project1.issue_set.create(title="issue4", creator=self.user2, assigned_to=self.user, status="CP")
        self.issue5 = self.project1.issue_set.create(title="issue5", creator=self.user, status="UA")

        self.tag1 = Tag.objects.create(label="test label", color="AAAAAA")
        self.note1 = Note.objects.create(label="test note", issue=self.issue1, creator=self.user)
        self.note2 = Note.objects.create(label="test note 2", issue=self.issue1, creator=self.user2)

        self.commit1 = Commit.objects.create(revision="somesha1sum", issue=self.issue1)

        self.client.login(username='john', password='johnpassword')

        self.project2 = Project.objects.create(name="project2", slug="project2", status="AC", priority=-1,
                                               scm_owner="owner", scm_repo="repo", scm_type="GH")
        self.issue6 = self.project2.issue_set.create(title="this is issue6", creator=self.user2, assigned_to=self.user, status="UA")
        self.commit2 = Commit.objects.create(revision="somesha1sum", issue=self.issue6)

        self.milestone1 = Milestone.objects.create(project=self.project2, deadline="3000-1-1")
        self.issue6.milestone = self.milestone1
        self.issue6.save()

        self.project3 = Project.objects.create(name="project3", slug="project3", status="CP", priority=-1,
                                               scm_owner="owner", scm_repo="repo", scm_type="BB")
        self.issue7 = self.project3.issue_set.create(title="issue7", creator=self.user2, assigned_to=self.user, status="UA")
        self.commit3 = Commit.objects.create(revision="somesha1sum", issue=self.issue7)

    def test_project_detail_view_200(self):
        response = self.client.get(reverse('project_detail', args=(str(self.project1.slug), )))
        self.assertEqual(response.status_code, 200, "ProjectDetailView should respond with HTTP 200 OK")
        self.assertEqual(self.project1.get_scm_url(), None, "Method get_scm_url for no SCM is not returning the expected string.")

        response = self.client.get(reverse('project_detail', args=(str(self.project2.slug), )))
        self.assertEqual(response.status_code, 200, "ProjectDetailView should respond with HTTP 200 OK")
        self.assertEqual(
            self.project2.get_scm_url(), "https://github.com/owner/repo", "Method get_scm_url for github is not returning the expected string.")
        self.assertNotEqual(self.milestone1, None, "Creating milestone failed.")
        self.assertNotEqual(self.issue6.milestone, None, "Issue milestone setting failed.")

        response = self.client.get(reverse('project_detail', args=(str(self.project3.slug), )))
        self.assertEqual(response.status_code, 200, "ProjectDetailView should respond with HTTP 200 OK")
        self.assertEqual(self.project3.get_scm_url(
        ), "https://bitbucket.org/owner/repo", "Method get_scm_url for bitbucket is not returning the expected string.")

    def test_project_detail_view_200_while_not_logged_in(self):
        self.client.logout()
        response = self.client.get(reverse('project_detail', args=(str(self.project1.slug), )))
        self.assertEqual(response.status_code, 200, "ProjectDetailView should respond with HTTP 200 OK while logged out")

    def test_project_detail_view_filter_in_kwargs(self):
        response = self.client.get(reverse('project_detail', args=(str(self.project1.slug), str(self.issue1.status))))
        self.assertEqual(response.context_data['filter'], self.issue1.status, "Issue page cannot sort for issues that have the status AS")

        response = self.client.get(reverse('project_detail', args=(str(self.project1.slug), str(self.issue2.status))))
        self.assertEqual(response.context_data['filter'], self.issue2.status, "Issue page cannot sort for issues that have the status UA")

        response = self.client.get(reverse('project_detail', args=(str(self.project1.slug), str(self.issue3.status))))
        self.assertEqual(response.context_data['filter'], self.issue3.status, "Issue page cannot sort for issues that have the status IP")

        response = self.client.get(reverse('project_detail', args=(str(self.project1.slug), str(self.issue4.status))))
        self.assertEqual(response.context_data['filter'], self.issue4.status, "Issue page cannot sort for issues that have the status CP")

        response = self.client.get(reverse('project_detail', args=(str(self.project1.slug), str(self.issue5.status))))
        self.assertEqual(response.context_data['filter'], self.issue5.status, "Issue page cannot sort for issues that have the status CP")

        self.assertEqual(response.status_code, 200, "ProjectDetailView should respond with HTTP 200 OK")

    def test_tag_filtering(self):
        response = self.client.get(reverse('project_detail', args=(str(self.project1.slug), str(self.issue1.status))) + '?tag=1')
        self.assertEqual(response.context_data['filter'], self.issue1.status, "Issue page cannot sort for issues that have the status AS")
        self.assertEqual(response.status_code, 200, "ProjectDetailView should respond with HTTP 200 OK")


class TagCreateViewTest(TestCase):
    def setUp(self):
        self.project1 = Project.objects.create(name="project1", slug="project1", status="AC", priority=-1)

    def test_tag_create(self):
        response = self.client.post(reverse('tag_create_view', ), {'label': 'User Interface', 'color': 'AAAAAA'})
        tag = Tag.objects.get(label="User Interface")
        self.assertEqual(tag.label, "User Interface", "New tag wasn't inserted successfully")
        self.assertEqual(response.status_code, 200, "TagCreateView should respond with HTTP 200 OK")


class TabUpdateViewTest(TestCase):
    def setUp(self):
        self.project1 = Project.objects.create(name="project1", slug="project1", status="AC", priority=-1)
        self.tag1 = Tag.objects.create(label="test label", color="AAAAAA")

    def test_tag_update_valid(self):
        response = self.client.post(
            reverse('tag_update_view', args=(self.tag1.pk, )), {'label': 'User Interface', 'color': 'BBBBBB'})
        self.assertEqual(response.status_code, 200, "TagUpdateView should respond with HTTP 200 OK")

    def test_tag_update_invalid(self):
        response = self.client.post(
            reverse('tag_update_view', args=(self.tag1.pk, )), {'label': 'User Interface', 'color': ""})
        self.assertEqual(response.status_code, 200, "TagUpdateView should respond with HTTP 200 OK")


class IssueDetailViewTest(TestCase):
    def setUp(self):
        self.project1 = Project.objects.create(name="project1", slug="project1", status="AC", priority=-1)
        self.user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
        self.user2 = User.objects.create_user('jake', 'jakelennon@thebeatles.com', 'jakepassword')
        self.issue1 = self.project1.issue_set.create(title="issue1", creator=self.user, assigned_to=self.user, status="AS")

    def test_update_issue_success(self):
        form_data = {str(
            self.issue1.pk) + '-title': 'NewTitle', str(self.issue1.pk) + '-description': 'NewDescription', str(self.issue1.pk) + '-assigned_to': str(self.user2.pk),
            'milestone_date': '2014-01-01', str(self.issue1.pk) + '-days_estimate': 5, }
        response = self.client.post(reverse('issue_detail', args=(str(self.issue1.pk),)), form_data)

        self.issue1 = Issue.objects.get(pk=self.issue1.pk)

        self.assertEqual(self.issue1.title, "NewTitle", "The issue title didn't update successfully")
        self.assertEqual(self.issue1.description, "NewDescription", "The issue title didn't update successfully")
        self.assertEqual(self.issue1.assigned_to, self.user2, "The issue assigned_to didn't update successfully")
        self.assertEqual(str(self.issue1.milestone.deadline), "2014-01-01", "The issue milestone didn't update successfully")
        self.assertEqual(str(self.issue1.days_estimate), "5", "The issue days_estimate didn't update successfully")
        self.assertEqual(response.status_code, 200, "IssueDetailView should respond with HTTP 200 OK")

        self.issue1.assigned_to = None
        self.issue1.save()
        self.assertEqual(self.issue1.assigned_to, None, "The issue assigned_to None didn't update successfully")
        self.assertEqual(self.issue1.status, 'UA', "The issue status did not reset successfully")

        self.issue1.status = "DL"
        self.issue1.save()
        self.assertEqual(self.issue1.assigned_to, None, "The issue Delete didn't update the assigned_to successfully")
        self.assertEqual(self.issue1.priority, -1, "The issue Delete didn't update the priority successfully")

    def test_status_in_self_request_POST(self):
        form_data = {'status': 'IP'}
        response = self.client.post(reverse('issue_detail', args=(str(self.issue1.pk),)), form_data)

        self.issue1 = Issue.objects.get(pk=self.issue1.pk)
        self.assertEqual(self.issue1.status, "IP", "The issue status didn't update successfully")
        self.assertEqual(response.status_code, 200, "IssueDetailView should respond with HTTP 200 OK")

    def test_approved_by_in_self_request_POST(self):
        form_data = {'status': 'CP', 'approved_by': str(self.user2.pk)}
        response = self.client.post(reverse('issue_detail', args=(str(self.issue1.pk),)), form_data)

        self.issue1 = Issue.objects.get(pk=self.issue1.pk)
        self.assertEqual(self.issue1.status, "CP", "The issue status didn't update successfully")
        self.assertEqual(self.issue1.approved_by, self.user2, "The issue approved_by didn't update successfully")
        self.assertEqual(response.status_code, 200, "IssueDetailView should respond with HTTP 200 OK")

    def test_form_invalid(self):
        form_data = {str(
            self.issue1.pk) + '-title': 'NewTitle', str(self.issue1.pk) + '-description': 'NewDescription', str(self.issue1.pk) + '-assigned_to': "aa",
            'milestone_date': '2014-01-01', str(self.issue1.pk) + '-days_estimate': "f", }
        response = self.client.post(reverse('issue_detail', args=(str(self.issue1.pk),)), form_data)

        response_data = json.JSONDecoder().decode(response.content)  # parses json string into a python dict
        self.assertEqual(response_data['status'], 'error', "HttpResponse should return an error for this test case")
        self.assertEqual(response.status_code, 200, "IssueDetailView should respond with HTTP 200 OK")


class CommitCreateViewTest(TestCase):
    def setUp(self):
        self.project1 = Project.objects.create(name="project1", slug="project1", status="AC", priority=-1)
        self.user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
        self.issue1 = self.project1.issue_set.create(title="issue1", creator=self.user, assigned_to=self.user, status="IP")

    def test_form_valid(self):
        form_data = {'revision': 'aaaaabbbbbccccc', 'issue': str(self.issue1.pk)}
        response = self.client.post(reverse('commit_create_view', args=(str(self.issue1.pk), )), form_data)

        self.issue1 = Issue.objects.get(pk=self.issue1.pk)

        response_data = json.JSONDecoder().decode(response.content)  # parses json string into a python dict
        self.assertEqual(self.issue1.commit_set.all()[0].revision, 'aaaaabbbbbccccc', "The commit revision wasn't created correctly")
        self.assertEqual(response_data['status'], 'success', "HttpResponse should return success for this test case")
        self.assertEqual(response.status_code, 200, "CommitCreateView should respond with HTTP 200 OK")

    def test_form_invalid(self):
        form_data = {'revision': 'aaaaabbbbbccccc', 'issue': ""}
        response = self.client.post(reverse('commit_create_view', args=(str(self.issue1.pk), )), form_data)

        response_data = json.JSONDecoder().decode(response.content)  # parses json string into a python dict
        self.assertEqual(response_data['status'], 'error', "HttpResponse should return error for this test case")
        self.assertEqual(response.status_code, 200, "CommitCreateView should respond with HTTP 200 OK")


class NoteCreateViewTest(TestCase):
    def setUp(self):
        self.project1 = Project.objects.create(name="project1", slug="project1", status="AC", priority=-1)
        self.user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
        self.issue1 = self.project1.issue_set.create(title="issue1", creator=self.user, assigned_to=self.user, status="IP")

    def test_create_new_note(self):
        form_data = {'label': 'NewNoteLabel', 'issue': str(self.issue1.pk), 'creator': str(self.user.pk), }
        response = self.client.post(reverse('note_create_view', args=(str(self.issue1.pk), )), form_data)

        response_data = json.JSONDecoder().decode(response.content)  # parses json string into a python dict
        self.assertEqual(response_data['status'], 'success', "HttpResponse should return success for this test case")
        self.assertEqual(response.status_code, 200, "CommitCreateView should respond with HTTP 200 OK")

    def test_form_invalid(self):
        form_data = {'label': 'NewNoteLabel', 'issue': "", 'creator': "", }
        response = self.client.post(reverse('note_create_view', args=(str(self.issue1.pk), )), form_data)

        response_data = json.JSONDecoder().decode(response.content)  # parses json string into a python dict
        self.assertEqual(response_data['status'], 'error', "HttpResponse should return error for this test case")
        self.assertEqual(response.status_code, 200, "CommitCreateView should respond with HTTP 200 OK")


class SortIssuesTest(TestCase):
    def setUp(self):
        self.project1 = Project.objects.create(name="project1", slug="project1", status="AC", priority=-1)
        self.user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
        self.issue1 = self.project1.issue_set.create(title="issue1", creator=self.user, assigned_to=self.user, status="UA")
        self.issue2 = self.project1.issue_set.create(title="issue2", creator=self.user, assigned_to=self.user, status="AS")
        self.issue3 = self.project1.issue_set.create(title="issue3", creator=self.user, assigned_to=self.user, status="IP")
        self.issue4 = self.project1.issue_set.create(title="issue4", creator=self.user, assigned_to=self.user, status="AS")
        self.issue5 = self.project1.issue_set.create(title="issue5", creator=self.user, assigned_to=self.user, status="UA")

    def test_sort_issue(self):
        form_data = {str(self.issue5.pk): '5', str(self.issue4.pk): '4', str(self.issue3.pk): '3', str(self.issue2.pk): '2', str(
            self.issue1.pk): '1', }
        response = self.client.post(reverse('sort_issue', args=(str(self.project1.slug), )), form_data)

        self.issue1 = Issue.objects.get(pk=self.issue1.pk)
        self.issue5 = Issue.objects.get(pk=self.issue5.pk)

        self.assertEqual(self.issue1.priority, 1, "Issue1's priority should be 1")
        self.assertEqual(self.issue5.priority, 5, "Issue5's priority should be 5")
        self.assertEqual(response.status_code, 200, "def sort_issue should respond with HTTP 200 OK")


class NewIssueTest(TestCase):
    def setUp(self):
        self.project1 = Project.objects.create(name="project1", slug="project1", status="AC", priority=-1)
        self.user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
        self.tag1 = Tag.objects.create(label="testtag1", color="AAAAAA")
        self.tag2 = Tag.objects.create(label="testtag2", color="BBBBBB")
        self.client.login(username='john', password='johnpassword')

    def test_create_new_issue(self):
        form_data = {'title': 'NewTitle', 'description': 'NewDescription', 'assigned_to': str(
            self.user.pk), 'milestone_date': '2014-01-01', 'tags': [str(self.tag1.pk), str(self.tag2.pk)]}
        response = self.client.post(reverse('new_issue', args=(str(self.project1.slug), )), form_data)

        new_issue = Issue.objects.get(title="NewTitle")

        self.assertEqual(new_issue.title, "NewTitle", "Issue title didn't get saved correctly")
        self.assertEqual(new_issue.description, "NewDescription", "Issue description didn't get saved correctly")
        self.assertEqual(new_issue.assigned_to, self.user, "Issue user didn't get saved correctly")
        self.assertEqual(str(new_issue.milestone.deadline), "2014-01-01", "Issue milestone didn't update successfully")
        self.assertEqual(new_issue.tags.all()[0], self.tag1, "tag1 didn't append to the new issue successfully")
        self.assertEqual(new_issue.tags.all()[1], self.tag2, "tag2 didn't append to the new issue successfully")
        response_data = json.JSONDecoder().decode(response.content)  # parses json string into a python dict
        self.assertEqual(response_data['status'], 'success', "HttpResponse should return success for this test case")
        self.assertEqual(response.status_code, 200, "def new_issue should respond with HTTP 200 OK")

    def test_create_new_issue__issue_status_UA(self):
        form_data = {'title': 'NewTitle', 'description': 'NewDescription', 'milestone_date': '2014-01-01', 'tags': [str(self.tag1.pk),
                                                                                                                    str(self.tag2.pk)]}
        response = self.client.post(reverse('new_issue', args=(str(self.project1.slug), )), form_data)

        new_issue = Issue.objects.get(title="NewTitle")

        self.assertEqual(new_issue.title, "NewTitle", "Issue title didn't get saved correctly")
        self.assertEqual(new_issue.description, "NewDescription", "Issue description didn't get saved correctly")
        self.assertEqual(str(new_issue.milestone.deadline), "2014-01-01", "Issue milestone didn't update successfully")
        self.assertEqual(new_issue.tags.all()[0], self.tag1, "tag1 didn't append to the new issue successfully")
        self.assertEqual(new_issue.tags.all()[1], self.tag2, "tag2 didn't append to the new issue successfully")
        response_data = json.JSONDecoder().decode(response.content)  # parses json string into a python dict
        self.assertEqual(response_data['status'], 'success', "HttpResponse should return success for this test case")
        self.assertEqual(response.status_code, 200, "def new_issue should respond with HTTP 200 OK")

    def test_create_new_issue_failure(self):
        form_data = {'title': "", 'description': 'NewDescription', 'assigned_to': 'a', 'tags': [str(self.tag1.pk), str(self.tag2.pk)]}
        response = self.client.post(reverse('new_issue', args=(str(self.project1.slug), )), form_data)

        response_data = json.JSONDecoder().decode(response.content)  # parses json string into a python dict
        self.assertEqual(response_data['status'], 'error', "HttpResponse should return error for this test case")
        self.assertEqual(response.status_code, 200, "def new_issue should respond with HTTP 200 OK")


@override_settings(USE_TZ=False)
class BurndownChartTest(TestCase):
    def setUp(self):
        self.ancient_past = datetime.datetime(1985, 11, 5)
        self.one_day = datetime.timedelta(days=1)

        self.user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')

        self.project1 = Project.objects.create(name="project1", slug="project1", status="AC", priority=-1)
        self.milestone1 = Milestone.objects.create(project=self.project1, deadline=self.ancient_past)
        self.milestone2 = Milestone.objects.create(project=self.project1, deadline=datetime.datetime.now() + self.one_day * 7)

        self.issue1 = self.project1.issue_set.create(title="issue1", creator=self.user, assigned_to=self.user, status="AS", milestone=self.milestone1)
        self.issue2 = self.project1.issue_set.create(title="issue2", creator=self.user, assigned_to=self.user, status="UA", milestone=self.milestone1)
        self.issue3 = self.project1.issue_set.create(title="issue3", creator=self.user, assigned_to=self.user, status="IP", milestone=self.milestone1)
        self.issue4 = self.project1.issue_set.create(title="issue4", creator=self.user, assigned_to=self.user, status="AS",
                                                     milestone=self.milestone1, close_date=self.ancient_past - self.one_day * 20)
        self.issue5 = self.project1.issue_set.create(title="issue5", creator=self.user, status="UA", milestone=self.milestone1)
        self.issue6 = self.project1.issue_set.create(title="issue6", creator=self.user, assigned_to=self.user, status="AS", milestone=self.milestone2)

        self.client.login(username='john', password='johnpassword')

    def test_chart_url_responds_200(self):
        response = self.client.get(self.milestone2.get_chart_url())
        self.assertEqual(response.status_code, 200, "BurndownChartView respond with HTTP 200 OK")

    def test_chart_with_past_date(self):
        data = self.milestone1.calculate_burndown_chart(when=self.milestone1.deadline - self.one_day * 10)
        self.assertEqual(data.get('slope'), 1.0 / 11.0, "slope should be 1/11")

    def test_chart_with_same_date(self):
        data = self.milestone1.calculate_burndown_chart(when=self.milestone1.deadline)
        self.assertEqual(data.get('slope'), 1.0 / 21.0, "slope should be 1/21")

    def test_chart_with_future_date(self):
        data = self.milestone1.calculate_burndown_chart(when=self.milestone1.deadline + self.one_day * 10)
        self.assertEqual(data.get('slope'), 1.0 / 31.0, "slope should be 1/31")

    def test_chart_with_no_closed_issues(self):
        self.issue4.delete()
        data = self.milestone1.calculate_burndown_chart(when=self.milestone1.deadline)
        self.assertEqual(data.get('optimal_slope'), 1.0, "optimal_slope should be 1/1")

    def test_chart_with_all_closed_issues(self):
        for issue in self.milestone1.issue_set.all():
            issue.status = 'CP'
            issue.save()
        data = self.milestone1.calculate_burndown_chart(when=self.milestone1.deadline)
        self.assertEqual(data.get('slope'), 1.0, "slope should be 1/1")
