from django.forms import ModelForm
from issues.models import Issue, Project, Note, Commit, IssueViewed, Tag
from django.contrib.auth.models import User


class IssueForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(IssueForm, self).__init__(*args, **kwargs)
        self.fields['assigned_to'].choices = [('', 10 * '-')] + [(u.pk, u.get_full_name()) for u in User.objects.filter(is_active=True)
                                                                 .order_by('first_name')]

    class Meta:
        model = Issue
        fields = ('title', 'description', 'assigned_to', 'milestone', 'days_estimate', 'tags')


class IssueStatusForm(ModelForm):

    class Meta:
        model = Issue
        fields = ('status',)


class IssueCloseForm(ModelForm):

    class Meta:
        model = Issue
        fields = ('status', 'approved_by')


class ProjectForm(ModelForm):

#    def __init__(self, *args, **kwargs):
#        super(IssueForm, self).__init__(*args, **kwargs)
# self.fields['assigned_to'].choices = [('', 10*'-')] + [(u.pk,
# u.get_full_name()) for u in
# User.objects.filter(is_active=True).order_by('first_name')]

    class Meta:
        model = Project
        fields = ('name', 'slug', 'priority', 'status')


class CommitForm(ModelForm):

    class Meta:
        model = Commit
        fields = ('revision', 'issue')


class TagForm(ModelForm):

    class Meta:
        model = Tag
        fields = ('color', )


class NoteForm(ModelForm):

    class Meta:
        model = Note
        fields = ('label', 'issue', 'creator')


class IssueViewedForm(ModelForm):

    class Meta:
        model = IssueViewed
        fields = ('last_viewed', )
