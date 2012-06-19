from django.forms import ModelForm
from issues.models import Issue

class IssueForm(ModelForm):
    class Meta:
        model = Issue
        fields = ('title', 'description', 'type', 'assigned_to', 'milestone', 'days_estimate')

class IssueCloseForm(ModelForm):
    class Meta:
        model = Issue
        fields = ('closed_by_revision',)
