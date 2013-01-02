import datetime
from django.db import models
from django.db.models import Q
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

    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, unique=True)
    status = models.CharField(max_length="64", default='AC', choices=STATUS_CHOICES)

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
    notes = models.CharField(max_length="1000", blank=True, null=True)
    issue_group = models.ForeignKey('IssueGroup', blank=True, null=True)

    class Meta:
        ordering = ['project', '-priority']

    def save(self, *args, **kwargs):
        try:
            old = Issue.objects.get(pk=self.pk)
            if self.status == 'DL' and old.status != 'DL':
                self.close_date = datetime.datetime.now()
                self.priority = -1
                self.assigned_to = None
            elif self.status == 'CP' and old.status != 'CP':
                print "%"*80
                self.close_date = datetime.datetime.now()
            elif self.assigned_to is None and old.assigned_to is not None:
                self.status = "UA"
            elif self.assigned_to != old.assigned_to:
                self.status = "AS"
        except Issue.DoesNotExist:
            pass
        super(Issue, self).save(*args, **kwargs)

    def close(self, revision, when=None):
        if not when:
            when = datetime.datetime.now().date()
        self.close_date = when
        self.save()

    def form_class(self):
        from issues.forms import IssueForm
        return IssueForm

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

    @models.permalink
    def get_absolute_url(self):
        return ('issue_detail', (), {'slug': self.project.slug, 'pk': self.id})

    def __unicode__(self):
        return self.title


class Commit(models.Model):
    revision = models.CharField(max_length=40)
    issue = models.ForeignKey(Issue)

    def __unicode__(self):
        return self.revision


class IssueGroup(models.Model):
    parent = models.ForeignKey('Issue')


class UserMethods(User):
    def assigned_issues(self):
        return self.issue_set.filter(status='AS')

    def inprogress_issues(self):
        return self.issue_set.filter(status='IP')

    def completed_issues(self):
        return self.issue_set.filter(status='CP').order_by('-close_date')

    def last_completed(self):
        completed = self.issue_set.filter(status='CP').order_by('-close_date')
        print completed.count()
        if (completed.count() > 0):
            return completed[0]
        else:
            return None

    def needs_review_issues(self):
        return self.issue_set.filter(status='NR').order_by('close_date')

    class Meta:
        proxy = True


class Milestone(models.Model):
    project = models.ForeignKey(Project)
    deadline = models.DateTimeField(default=datetime.datetime.now)

    @models.permalink
    def get_chart_url(self):
        return ('burndown_chart', (), {'slug': self.project.slug, 'pk': self.pk})

    def __unicode__(self):
        return str(self.deadline.date())
