from django.db import models
from django.db.models import Q
from django.utils.timezone import now
from django.contrib.auth.models import User
from django.utils.safestring import SafeString


class Tag(models.Model):
    label = models.CharField(max_length=32)
    color = models.CharField(max_length=6)

    def __unicode__(self):
        return self.label


class Project(models.Model):

    STATUS_CHOICES = (
        ('AC', 'Active'),
        ('IN', 'Inactive'),
        ('FZ', 'Frozen'),
        ('CP', 'Completed'),
    )

    SCM_CHOICES = (
        ('GH', 'GitHub'),
        ('BB', 'BitBucket'),
    )

    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, unique=True)
    status = models.CharField(max_length="64", default='AC', choices=STATUS_CHOICES)
    scm_owner = models.CharField(max_length=64, null=True, blank=True)
    scm_repo = models.CharField(max_length=64, null=True, blank=True)
    scm_type = models.CharField(max_length="64", default='GH', choices=SCM_CHOICES, null=True, blank=True)
    priority = models.IntegerField(default=-1, blank=False, null=False)

    class Meta:
        ordering = ['-priority']

    def __unicode__(self):
        return self.name

    def as_a(self):
        return SafeString('<a href="%s">%s</a>' % (self.get_absolute_url(), self.__unicode__()))

    def open_issues(self):
        return Issue.objects.filter(project=self).exclude(status='DL').exclude(status='NR').exclude(status='CP')

    def get_tags(self):
        # we should filter by project...
        return Tag.objects.all()  # filter(project=self)

    def closed_issues(self):
        return Issue.objects.filter(project=self, ).order_by('-close_date')

    def filtered_issues(self, status_filter):
        return Issue.objects.filter(project=self, status=status_filter)

    @models.permalink
    def get_absolute_url(self):
        return ('project_detail', (), {'slug': self.slug})

    def recently_completed_issues(self):
        return self.issue_set.filter(status='CP').order_by('-close_date')

    def unassigned_issues(self):
        return self.issue_set.filter(status="UA").order_by('-pk')

    def assigned_issues(self):
        return self.issue_set.filter(status="AS")

    def recently_deleted_issues(self):
        return self.issue_set.filter(status="DL").order_by('-close_date')

    def in_progress_issues(self):
        return self.issue_set.filter(status="IP")

    def needs_review_issues(self):
        return self.issue_set.filter(status="NR").order_by('close_date')

    def future_milestones(self):
        return self.milestone_set.filter(deadline__gte=now())

    def get_scm_url(self):
        if self.scm_owner and self.scm_repo:
            if self.scm_type == 'GH':
                return "https://github.com/" + self.scm_owner + "/" + self.scm_repo
            elif self.scm_type == 'BB':
                return "https://bitbucket.org/" + self.scm_owner + "/" + self.scm_repo
        return None

    def save(self, *args, **kwargs):
        if self.status != "AC":
            self.priority = -1
        super(Project, self).save(*args, **kwargs)


class Issue(models.Model):

    STATUS_CHOICES = (
        ('AS', 'Assigned'),
        ('IP', 'In Progress'),
        ('UA', 'Unassigned'),
        ('CP', 'Completed'),
        ('NR', 'Needs Review'),
        ('DL', 'Deleted'),
    )

    title = models.CharField(max_length=1000)
    description = models.TextField(blank=True, null=True)
    priority = models.IntegerField(default=-1, blank=False, null=False)
    user_priority = models.IntegerField(default=-1, blank=False, null=False)
    creator = models.ForeignKey(User, related_name="+")
    assigned_to = models.ForeignKey(User, blank=True, null=True)
    approved_by = models.ForeignKey(User, blank=True, null=True, related_name="issue_approved_by")
    close_date = models.DateTimeField(blank=True, null=True)
    project = models.ForeignKey(Project, null=True)
    days_estimate = models.DecimalField(
        blank=True, null=True, max_digits=65, decimal_places=5, help_text="How many days will it take to complete e.g. 0.5")
    milestone = models.ForeignKey('Milestone', null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    status = models.CharField(max_length="64", blank=True, null=True, choices=STATUS_CHOICES)
    parent = models.ForeignKey('Issue', blank=True, null=True)
    created = models.DateTimeField(default=now)

    class Meta:
        ordering = ['project', '-priority']

    def save(self, *args, **kwargs):
        try:
            old = Issue.objects.get(pk=self.pk)
            if self.status != "AS":
                self.user_priority = -1
            if self.status == 'DL' and old.status != 'DL':
                self.close_date = now()
                self.priority = -1
                self.assigned_to = None
            elif self.status == 'CP' and old.status != 'CP':
                self.close_date = now()
            elif self.assigned_to is None and old.assigned_to is not None:
                self.status = "UA"
            elif self.assigned_to != old.assigned_to:
                self.status = "AS"
        except Issue.DoesNotExist:
            pass
        super(Issue, self).save(*args, **kwargs)

    def close(self, revision, when=None):
        if not when:
            when = now().date()
        self.close_date = when
        self.save()

    def form_class(self):
        from issues.forms import IssueForm
        return IssueForm

    def get_subissues(self):
        return Issue.objects.filter(parent=self).order_by('priority')

    def form_kwargs(self):
        return dict(instance=self, prefix=str(self.pk))

    def form(self, **kwargs):
        form_kwargs = self.form_kwargs()
        form_kwargs.update(kwargs)
        return self.form_class()(**form_kwargs)

    def close_form(self, **kwargs):
        from issues.forms import IssueCloseForm
        form_kwargs = self.form_kwargs()
        form_kwargs.update(kwargs)
        return IssueCloseForm(**form_kwargs)

    @property
    def has_children(self):
        return Issue.objects.filter(parent=self).count() > 0

    @models.permalink
    def get_absolute_url(self):
        return ('issue_detail', (), {'slug': self.project.slug, 'pk': self.id})

    def __unicode__(self):
        return self.title


class Commit(models.Model):
    revision = models.CharField(max_length=40)
    issue = models.ForeignKey(Issue)
    created = models.DateTimeField(default=now, auto_now_add=True)

    def get_url(self):
        if self.issue.project.scm_owner and self.issue.project.scm_repo:
            if self.issue.project.scm_type == 'GH':
                return "https://github.com/" + self.issue.project.scm_owner + "/" + self.issue.project.scm_repo + "/commit/" + self.revision
            elif self.issue.project.scm_type == 'BB':
                return "https://bitbucket.org/" + self.issue.project.scm_owner + "/" + self.issue.project.scm_repo + "/commits/" + self.revision
        return None

    def __unicode__(self):
        return self.revision


class UserMethods(User):
    def assigned_issues(self):
        return self.issue_set.filter(status='AS').order_by('-user_priority')

    def inprogress_issues(self):
        return self.issue_set.filter(status='IP')

    def completed_issues(self):
        return self.issue_set.filter(status='CP').order_by('-close_date')

    def last_completed(self):
        completed = self.issue_set.filter(status='CP').order_by('-close_date')
        if (completed.count() > 0):
            return completed[0]
        else:
            return None

    def needs_review_issues(self):
        return self.issue_set.filter(status='NR')

    class Meta:
        proxy = True


class Milestone(models.Model):
    project = models.ForeignKey(Project)
    deadline = models.DateField(default=now)

    @models.permalink
    def get_chart_url(self):
        return ('burndown_chart', (), {'slug': self.project.slug, 'pk': self.pk})

    def __unicode__(self):
        return str(self.deadline)


class Note(models.Model):
    label = models.CharField(max_length=1000)
    created = models.DateTimeField(default=now, auto_now_add=True)
    issue = models.ForeignKey('Issue', blank=True, null=True)
    creator = models.ForeignKey(User, related_name="+")

    def __unicode__(self):
        return self.label
