import datetime
from django.db import models
from django.db.models import Q, Count
from django.utils.timezone import now, utc
from django.contrib.auth.models import User
from django.utils.safestring import SafeString
from issues.helpers import day_range, days_of_work, days_apart, work_left, business_day_range, is_business_day


class Tag(models.Model):
    label = models.CharField(max_length=32)
    color = models.CharField(max_length=6)
    active = models.BooleanField(default=True)

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

    def filtered_issues(self, status_filter):
        return Issue.objects.filter(project=self, status=status_filter)

    @models.permalink
    def get_absolute_url(self):
        return ('project_detail', (), {'slug': self.slug})

    def recently_completed_issues(self):
        return self.issue_set.filter(status='CP').order_by('-close_date').exclude(close_date=None)

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

    @property
    def current_milestone(self):
        try:
            return self.future_milestones().annotate(issue_count=Count('issue')).exclude(issue_count=0).order_by('deadline')[0]
        except (Milestone.DoesNotExist, IndexError):
            return None

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
    created = models.DateTimeField(default=now)
    viewers = models.ManyToManyField(User, through='IssueViewed', related_name='viewer_set')

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

    def form_class(self):
        from issues.forms import IssueForm
        return IssueForm

    def form_kwargs(self):
        return dict(instance=self, prefix=str(self.pk))

    def form(self, **kwargs):
        form_kwargs = self.form_kwargs()
        form_kwargs.update(kwargs)
        return self.form_class()(**form_kwargs)

    def has_new_notes(self, viewing_user):
        if viewing_user.is_authenticated():
            notes = self.note_set.exclude(creator=viewing_user).order_by('-created')[:1]
            if notes:
                return IssueViewed.objects.filter(user=viewing_user, issue=self).exclude(last_viewed__lte=notes[0].created).count() == 0
        return False

    def get_notes(self):
        return self.note_set.all().order_by('created')

    @models.permalink
    def get_absolute_url(self):
        return ('issue_detail', (), {'pk': self.id})

    def __unicode__(self):
        return self.title


class Commit(models.Model):
    revision = models.CharField(max_length=40)
    issue = models.ForeignKey(Issue)
    created = models.DateTimeField(default=now)

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

    def all_milestones(self):
        return Milestone.objects.filter(deadline__gte=now(), project__in=self.issue_set.values_list('project', flat=True)).order_by('project')

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

    def calculate_burndown_chart(self, width=800, height=450, when=None):
        data = {}
        issues = self.issue_set.all()
        one_day = datetime.timedelta(days=1)
        if when is None:
            when = datetime.datetime.now()
        try:
            start_date = issues.filter(close_date__isnull=False).order_by('close_date')[0].close_date - one_day
        except IndexError:
            start_date = when

        end_date = datetime.datetime.combine(self.deadline, datetime.time(17))
        w = max(len(list(day_range(start_date, end_date))) - 1, 1)
        h = max(days_of_work(issues), 1)
        grid_w = width / w
        grid_h = height / h
        today_width = days_apart(start_date, when)
        start_height = work_left(issues, start_date - one_day)
        points = []
        for date, day in day_range(start_date, min(end_date, when)):
            point = (day, work_left(issues, date))
            points.append(point)
        # optimal "green" line
        try:
            optimal_slope = h / float(len(list(business_day_range(start_date + one_day, end_date))))
        except ZeroDivisionError:
            optimal_slope = 1.0
        optimal_line_points = []
        current_y = 0
        optimal_line_points.append((0, 0))
        for date, day in day_range(start_date + one_day, end_date):
            if is_business_day(date):
                current_y += optimal_slope
            point = (day + 1, current_y)
            optimal_line_points.append(point)
        data['optimal_line_points'] = [(x * grid_w, y * grid_h) for x, y in optimal_line_points]
        data['points'] = [(x * grid_w, y * grid_h) for x, y in points]
        if today_width != 0:
            slope = float(work_left(issues, when - one_day)) / today_width
        else:
            slope = 1
        if slope == 0:
            slope = 1
        data['projected'] = {
            'p1': {'x': 0, 'y': 0},
            'p2': {'x': float(h) / float(slope) * grid_w, 'y': h * grid_h}
        }
        # maximum x value
        data['width'] = w * grid_w
        # maximum y value
        data['height'] = h * grid_h
        # date of first closed issues
        data['start_date'] = start_date.date()
        # date that self ends
        data['end_date'] = end_date.date()
        # today's date
        data['today_date'] = when.date()
        # x value for today's date
        data['today_width'] = today_width * grid_w
        # list of x values for each day
        data['day_widths'] = [(x + 1) * grid_w for x in xrange(w)]
        # list of y values for each issue
        data['day_heights'] = [(y + 1) * grid_h for y in xrange(int(h))]
        # width of svg with padding
        data['svg_width'] = w * grid_w + 50
        # height of svg with padding.
        data['svg_height'] = h * grid_h + 40
        # slop of optimal line
        data['optimal_slope'] = optimal_slope
        # slop of predicted/actual line
        data['slope'] = slope
        return data

    class Meta:
        get_latest_by = 'deadline'


class Note(models.Model):
    label = models.CharField(max_length=1000)
    created = models.DateTimeField(default=now)
    issue = models.ForeignKey('Issue', blank=True, null=True)
    creator = models.ForeignKey(User, related_name="+")

    def __unicode__(self):
        return self.label


class IssueViewed(models.Model):
    issue = models.ForeignKey(Issue)
    user = models.ForeignKey(User)
    last_viewed = models.DateTimeField(default=now, blank=True)

