"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".
"""

from django.test import TestCase
from django.core.urlresolvers import reverse


class ProjectListViewTest(TestCase):
    def test_project_list_responds_200(self):
        """
        Tests that the ProjectListView responds with 200 OK.
        """
        response = self.client.get(reverse('project_list'))
        self.assertEqual(response.status_code, 200, "ProjectListView should respond with HTTP 200 OK")
