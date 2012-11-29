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
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50)
    def __unicode__(self):
        return self.name
    
    def as_a(self):
        return SafeString('<a href="%s">%s</a>' % (self.get_absolute_url(), self.__unicode__()))
    
    def open_issues(self):
        return Issue.objects.filter(project=self).filter(Q(closed_by_revision=u'') or Q(closed_by_revision__isnull=True))
    
    def closed_issues(self):
        return Issue.objects.filter(project=self).exclude(Q(closed_by_revision=u'') or Q(closed_by_revision__isnull=True)).order_by('-close_date')
    
    @models.permalink
    def get_absolute_url(self):
        return ('project_detail', (), {'slug': self.slug})
        
    def recently_closed_issues(self):
        return self.issue_set.filter(close_date__isnull=False).order_by('close_date')[:10]
        
    def unassigned_issues(self):
        return self.issue_set.filter(status="Unassigned").order_by('-pk')[:10]
        
    def assigned_issues(self):
        return self.issue_set.filter(status="Assigned")
        
    def recently_deleted_issues(self):
        return self.issue_set.filter(status="Deleted")[:10]

class Issue(models.Model):
    title = models.CharField(max_length=1000)
    description = models.TextField(blank=True, null=True)
    priority = models.IntegerField(default=-1, blank=False, null=False)
    creator = models.ForeignKey(User, related_name="+")
    assigned_to = models.ForeignKey(User, blank=True, null=True)
    closed_by_revision = models.CharField(max_length=1000, blank=True, null=True)
    close_date = models.DateTimeField(blank=True, null=True)
    project = models.ForeignKey(Project, null=True)
    days_estimate = models.DecimalField(blank=True, null=True, max_digits=65, decimal_places=5, help_text="How many days will it take to complete e.g. 0.5")
    milestone = models.ForeignKey('Milestone', null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    status = models.CharField(max_length="64", blank=True, null=True)
    notes = models.CharField(max_length="1000", blank=True, null=True)
    
    class Meta:
        ordering = ['project', 'closed_by_revision', '-priority']

    def save(self, *args, **kwargs):
        try:
            old = Issue.objects.get(pk=self.pk)
            #put status updates here
            print "%"*80
            if self.assigned_to == None:
               self.status = "Unassigned"
            else:
                self.status = "Assigned"
            if not old.closed_by_revision and self.closed_by_revision:
                self.close_date = datetime.datetime.now()
        except Issue.DoesNotExist:
            pass
        super(Issue, self).save(*args, **kwargs)

    def close(self, revision, when=None):
        if not when:
            when = datetime.datetime.now().date()
        self.closed_by_revision=int(revision)
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

class Milestone(models.Model):
    project = models.ForeignKey(Project)
    deadline = models.DateTimeField(default=datetime.datetime.now)

    @models.permalink
    def get_chart_url(self):
        return ('burndown_chart', (), {'slug': self.project.slug, 'pk': self.pk})

    def __unicode__(self):
        return str(self.deadline.date())

