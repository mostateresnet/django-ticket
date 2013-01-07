import datetime
import json
from django import forms
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, CreateView
from django.views.generic.base import TemplateView
from issues.models import Project, Issue, Milestone, Tag, UserMethods, Commit, Note
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Q
from django.db import transaction
from annoying.utils import HttpResponseReload
from issues.forms import IssueForm, IssueStatusForm, IssueCloseForm, ProjectForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User


class ProjectListView(ListView):
    queryset = Project.objects.all()

    def get_context_data(self, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)
        context['users'] = UserMethods.objects.filter(is_active=True)
        context['project_form'] = ProjectForm()
        return context


class UserListView(ListView):
    queryset = Project.objects.all()
    template_name = 'issues/user_profile.html'

    def get_context_data(self, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)

        if 'user_id' in self.kwargs:
            context['user_data'] = UserMethods.objects.get(pk=self.kwargs['user_id'])

    # UserMethods.objects.filter(pk=self.kwargs['user_id'])[0]

        return context


class ProjectNewView(CreateView):
    model = Project
    template_name = "issues/project_detail.html"

    def form_valid(self, form):
        project = form.save()
        return HttpResponse(json.dumps({'status': 'success', 'url': project.get_absolute_url()}), mimetype='application/json')

    def form_invalid(self, form):
        return HttpResponse(json.dumps({'status': 'error', 'message': form.errors.as_text()}), mimetype='application/json')


class ProjectSortView(UpdateView):
    @transaction.commit_on_success
    def post(self, *args, **kwargs):
        sorted_ids = self.request.POST.getlist('sorted_ids[]')
        i = len(sorted_ids)
        for id in sorted_ids:
            p = Project.objects.get(pk=id)
            p.priority = i
            p.save()
            i -= 1
        return HttpResponse("success")


class UserSortIssueView(UpdateView):
    @transaction.commit_on_success
    def post(self, *args, **kwargs):
        sorted_ids = self.request.POST.getlist('sorted_ids[]')
        i = len(sorted_ids)
        for id in sorted_ids:
            issue = Issue.objects.get(pk=id)
            issue.user_priority = i
            issue.save()
            i -= 1
        return HttpResponse("success")


class ProjectDetailView(DetailView):
    model = Project

    def get_template_names(self):
        project = self.object
        names = super(ProjectDetailView, self).get_template_names()
        names.insert(0, "issues/%s/project_detail.html" % (project.slug))
        return names

    def get_context_data(self, **kwargs):
        context = super(ProjectDetailView, self).get_context_data(**kwargs)
        context['issue_form'] = IssueForm()

        if 'filter' in self.kwargs:
            context['issues'] = self.object.filtered_issues(self.kwargs['filter'])
            context['filter'] = self.kwargs['filter']
        else:
            context['issues'] = self.object.open_issues()
            context['filter'] = "OPEN"

        context['issues'] = context['issues'].filter(parent__isnull=True)
        context['tags'] = self.object.get_tags()
        return context


class TagCreateView(CreateView):
    model = Tag

    def form_valid(self, form):
        pk_id = form.save().pk
        return HttpResponse(json.dumps({'status': 'success', 'id': pk_id}), mimetype='application/json')


class TagUpdateView(UpdateView):
    model = Tag

    def form_valid(self, form):
        pk_id = form.save().pk
        return HttpResponse(json.dumps({'status': 'success', 'id': pk_id}), mimetype='application/json')

    def form_invalid(self, form):
        pk_id = form.save().pk
        return HttpResponse(json.dumps({'status': 'error', 'id': pk_id}), mimetype='application/json')


class IssueDetailView(UpdateView):
    model = Issue

    def get_form_class(self):
        if 'approved_by' in self.request.POST:
            return IssueCloseForm
        if 'status' in self.request.POST:
            return IssueStatusForm
        else:
            return self.object.form_class()

    def get_form_kwargs(self):
        if 'status' in self.request.POST:
            return super(IssueDetailView, self).get_form_kwargs()
        else:
            kwargs = super(IssueDetailView, self).get_form_kwargs()
            kwargs.update(self.object.form_kwargs())
            return kwargs

    def form_valid(self, form):
        project = form.save()
        return HttpResponse(json.dumps({'status': 'success', 'url': project.get_absolute_url()}), mimetype='application/json')

    def form_invalid(self, form):
        print dir(form.errors)
        return HttpResponse(json.dumps({'status': 'error', 'errors': form.errors}), mimetype='application/json')


class CommitCreateView(CreateView):
    model = Commit

    def form_valid(self, form):
        pk_id = form.save().pk
        return HttpResponse(json.dumps({'status': 'success', 'id': pk_id}), mimetype='application/json')


class NoteCreateView(CreateView):
    model = Note

    def form_valid(self, form):
        pk_id = form.save().pk
        return HttpResponse(json.dumps({'status': 'success', 'id': pk_id}), mimetype='application/json')


def issue_detail(request, slug, id):
#    project = Project.objects.get(slug=slug)
    issue = Issue.objects.get(id=id)
    issue.save()
    return HttpResponse("success")


def sort_issue(request, slug):
    project = Project.objects.get(slug=slug)
    for id, priority in request.POST.items():
        issue = Issue.objects.get(id=id)
        issue.priority = priority
        issue.save()
    return HttpResponse("success")


@login_required
def new_issue(request, slug):
    project = Project.objects.get(slug=slug)
    form = IssueForm(request.POST)
    if form.is_valid():
        issue = form.save(commit=False)
        issue.priority = 0
        issue.creator = request.user
        issue.project = project

        if (issue.assigned_to):
            issue.status = 'AS'
        else:
            issue.status = 'UA'

        issue.save()
        form.save_m2m()
        return HttpResponse(json.dumps({'status': 'success', 'url': project.get_absolute_url()}), mimetype='application/json')
    else:
        return HttpResponse(json.dumps({'status': 'error', 'errors': form.errors}), mimetype='application/json')


def days_apart(start_date, end_date):
    """ Return the number of days apart between two datetimes

    >>> day1 = datetime.datetime(year=2011, month=9, day = 29)
    >>> day2 = datetime.datetime(year=2011, month=10, day = 3)
    >>> days_apart(day1, day2)
    4
    """
    return (end_date.date() - start_date.date()).days


def day_range(start_date, end_date):
    """ Given two dates, generate (date, day#) pairs for all the days in the
    range, inclusive

    >>> day1 = datetime.datetime(year=2011, month=9, day = 29)
    >>> day2 = datetime.datetime(year=2011, month=10, day = 3)
    >>> list(day_range(day1, day2))
    [(datetime.date(2011, 9, 29), 0), (datetime.date(2011, 9, 30), 1), (datetime.dat
    e(2011, 10, 1), 2), (datetime.date(2011, 10, 2), 3)]
    """
    for day in range(days_apart(start_date, end_date) + 1):
        date = start_date.date() + datetime.timedelta(days=day)
        yield date, day


def is_business_day(date):
    return date.weekday() <= 4


def business_day_range(start_date, end_date):
    """ Given two dates, generate (date, day#) pairs for all the business days in
    the range, inclusive

    >>> day1 = datetime.datetime(year=2011, month=5, day = 31)
    >>> day2 = datetime.datetime(year=2011, month=6, day = 6)
    >>> list(business_day_range(day1, day2))
    [(datetime.date(2011, 5, 31), 0), (datetime.date(2011, 6, 1), 1),
    (datetime.date(2011, 6, 2), 2), (datetime.date(2011, 6, 3), 3)]
    """
    for date, day in day_range(start_date, end_date):
        if is_business_day(date):
            yield date, day


def business_weeks(start_date, end_date):
    """ Given two dates, generate (date1, date2, ...) for all contiguous business days in
    the range.
    >>> day1 = datetime.datetime(year=2012, month=4, day = 16)
    >>> day2 = datetime.datetime(year=2012, month=4, day = 23)
    >>> list(business_weeks(day1, day2)

    """
    week = []
    for date, day in day_range(start_date, end_date):
        if is_business_day(date):
            week.append((date, day))
        elif week:
            yield tuple(week)
            week = []
    if week:
        yield tuple(week)


def days_of_work(issues):
    """Given a queryset of issues, return the number of days it is estimated
    to complete all of them."""
    return float(sum(i or 1 for i in issues.values_list('days_estimate', flat=True)))


def work_left(issues, date):
    """Given a queryset of issues, return how many days of work is
    estimated to complete all of them excluding completed issues on or before
    a given date"""
    one_day = datetime.timedelta(days=1)
    return days_of_work(issues.exclude(Q(close_date__isnull=True) | Q(close_date__gt=date + one_day)))


class BurndownChartView(DetailView):
    model = Milestone

    def get_template_names(self):
        return ["issues/%s/burndown.svg" % self.object.project.slug, "issues/burndown.svg"]

    def get_context_data(self, **kwargs):
        context = super(BurndownChartView, self).get_context_data(**kwargs)
        milestone = self.object
        issues = milestone.issue_set.all()
        one_day = datetime.timedelta(days=1)
        try:
            start_date = issues.filter(close_date__isnull=False).order_by('close_date')[0].close_date - one_day
        except IndexError:
            start_date = datetime.datetime.now()

        end_date = milestone.deadline
        now = datetime.datetime.now()
        width = len(list(day_range(start_date, end_date))) - 1
        height = days_of_work(issues)
        grid_w = 500 / width
        grid_h = 500 / height
        today_width = days_apart(start_date, now)
        start_height = work_left(issues, start_date - one_day)
        points = []
        for date, day in day_range(start_date, min(end_date, now)):
            point = (day, work_left(issues, date))
            points.append(point)
        # optimal "green" line
        try:
            optimal_slope = height / float(len(list(business_day_range(start_date + one_day, end_date))))
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
        context['optimal_line_points'] = [(x * grid_w, y * grid_h) for x, y in optimal_line_points]
        context['points'] = [(x * grid_w, y * grid_h) for x, y in points]
        if today_width != 0:
            slope = float(work_left(issues, now - one_day)) / today_width
        else:
            slope = 1
        if slope == 0:
            slope = 1
        context['projected'] = {
            'p1': {'x': 0, 'y': 0},
            'p2': {'x': float(height) / float(slope) * grid_w, 'y': height * grid_h}
        }
        # maximum x value
        context['width'] = width * grid_w
        # maximum y value
        context['height'] = height * grid_h
        # date of first closed issues
        context['start_date'] = start_date.date()
        # date that milestone ends
        context['end_date'] = end_date.date()
        # today's date
        context['today_date'] = datetime.datetime.now().date()
        # x value for today's date
        context['today_width'] = today_width * grid_w
        # list of x values for each day
        context['day_widths'] = [(x + 1) * grid_w for x in range(width)]
        # list of y values for each issue
        context['day_heights'] = [(y + 1) * grid_h for y in range(int(height))]
        # width of svg with padding
        context['svg_width'] = (width + 10) * grid_w
        # height of svg with padding.
        context['svg_height'] = (height + 10) * grid_h
        return context
