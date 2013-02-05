import datetime
import json
from django.utils import formats
from django.utils.timezone import now, utc, localtime
from django import forms
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, CreateView
from django.views.generic.base import TemplateView
from issues.models import Project, Issue, Milestone, Tag, UserMethods, Commit, Note, IssueViewed
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Q
from django.db import transaction
from annoying.utils import HttpResponseReload
from issues.forms import IssueForm, IssueStatusForm, IssueCloseForm, ProjectForm, NoteForm, CommitForm, IssueViewedForm, TagForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django import http
# from django.utils import simplejson as json


class JSONResponseMixin(object):
    def render_to_response(self, context):
        return self.get_json_response(self.convert_context_to_json(context))

    def get_json_response(self, content, **httpresponse_kwargs):
        return http.HttpResponse(content,
                                 content_type='application/json',
                                 **httpresponse_kwargs)

    def convert_context_to_json(self, context):
        return json.dumps(context)


class ProjectListView(ListView):
    queryset = Project.objects.all()

    def get_context_data(self, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)
        context['users'] = UserMethods.objects.filter(is_active=True)
        context['project_form'] = ProjectForm()
        context['tags'] = Tag.objects.all()
        return context


class UserListView(ListView):
    queryset = Project.objects.all()
    template_name = 'issues/user_profile.html'

    def get_context_data(self, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)
        context['tags'] = Tag.objects.all()

        if 'user_id' in self.kwargs:
            context['user_data'] = UserMethods.objects.get(pk=self.kwargs['user_id'])

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
        if self.request.user.is_authenticated():
            context['needs_review_issues'] = self.object.needs_review_issues().exclude(assigned_to=self.request.user)

        if 'filter' in self.kwargs:
            context['issues'] = self.object.filtered_issues(self.kwargs['filter'])
            context['filter'] = self.kwargs['filter']
        else:
            context['issues'] = self.object.open_issues()
            context['filter'] = "OPEN"

        tag_filter = self.request.GET.get('tag', '').split(',')
        if (tag_filter and '' not in tag_filter):
            context['issues'] = context['issues'].filter(tags__in=tag_filter).distinct()

        context['tags'] = self.object.get_tags()

        return context


class TagCreateView(CreateView):
    model = Tag

    def form_valid(self, form):
        pk_id = form.save().pk
        return HttpResponse(json.dumps({'status': 'success', 'id': pk_id, 'url': reverse('tag_update_view', args=[pk_id])}), mimetype='application/json')


class TagSearchView(JSONResponseMixin, ListView):

    searching = False

    def get_queryset(self):
        auto_complete_term = self.request.GET.get('term', '')
        if (auto_complete_term):
            self.searching = True
            return Tag.objects.filter(label__icontains=auto_complete_term)
        else:
            return Tag.objects.filter(label__iexact=self.request.GET.get('label', ''))

    def get_context_data(self, **kwargs):
        context = {}
        try:
            results = self.get_queryset()
            if (self.searching):
                context = list(results.values('label'))

            else:
                result = results[0]
                context['label'] = result.label
                context['pk'] = result.pk

        except IndexError:
            pass
        return context


class TagUpdateView(UpdateView):
    model = Tag

    def get_form_class(self):
        return TagForm

    def form_valid(self, form):
        pk_id = form.save().pk
        return HttpResponse(json.dumps({'status': 'success', 'id': pk_id}), mimetype='application/json')

    def form_invalid(self, form):
        return HttpResponse(json.dumps({'status': 'error', 'errors': form.errors}), mimetype='application/json')


class IssueDetailView(UpdateView):
    model = Issue

    def post(self, *args, **kwargs):
        if self.request.POST.get('milestone_date'):
            issue = Issue.objects.get(pk=kwargs['pk'])
            # call method that modifies post data for our custom milestone handling
            post_data = append_new_milestone(self.request.POST.copy(), issue.project, kwargs['pk'])
            self.request.POST = post_data

        self.request.POST = append_new_tags(self.request.POST.copy(), kwargs['pk'])

        response = super(IssueDetailView, self).post(*args, **kwargs)

        if 'viewed' in self.request.POST:
            IssueViewed.objects.filter(user=self.request.user, issue=self.object).delete()
            IssueViewed(user=self.request.user, issue=self.object).save()

        return response

    def get_form_class(self):
        if 'approved_by' in self.request.POST:
            return IssueCloseForm
        elif 'status' in self.request.POST:
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
        return HttpResponse(json.dumps({'status': 'error', 'errors': form.errors}), mimetype='application/json')


class CommitCreateView(CreateView):
    model = Commit

    def get_form_class(self):
        return CommitForm

    def form_valid(self, form):
        commit = form.save()
        return HttpResponse(json.dumps({'status': 'success', 'id': commit.pk, 'url': commit.get_url(), 'datetime': formats.date_format(localtime(commit.created), "SHORT_DATETIME_FORMAT")}), mimetype='application/json')

    def form_invalid(self, form):
        return HttpResponse(json.dumps({'status': 'error', 'errors': form.errors}), mimetype='application/json')


class NoteCreateView(CreateView):
    model = Note

    def get_form_class(self):
        return NoteForm

    def form_valid(self, form):
        note = form.save()
        return HttpResponse(json.dumps({'status': 'success', 'id': note.pk, 'datetime': formats.date_format(localtime(note.created), "SHORT_DATETIME_FORMAT")}), mimetype='application/json')

    def form_invalid(self, form):
        return HttpResponse(json.dumps({'status': 'error', 'errors': form.errors}), mimetype='application/json')


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
    if request.POST.get('milestone_date'):
        # call method that modifies post data for our custom milestone handling
        post_data = append_new_milestone(request.POST.copy(), project, None)
        request.POST = post_data

    request.POST = append_new_tags(request.POST.copy(), None)

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


def append_new_tags(POST_copy, issue_id):
    with transaction.commit_on_success():
        for ntag in POST_copy.getlist('new-tags'):
            tag_values = ntag.split(",")
            tag_result = Tag.objects.create(label=','.join(tag_values[:-1]).strip(), color=tag_values[-1])
            if (issue_id):
                tag_append = "%s-tags" % issue_id
            else:
                tag_append = "tags"

            POST_copy.appendlist(tag_append, tag_result.pk)
    return POST_copy

# method that modifies post data for our custom milestone handling


def append_new_milestone(POST_copy, project, issue_id):
    milestone_date = POST_copy['milestone_date']
    date = datetime.datetime.strptime(POST_copy['milestone_date'], '%Y-%m-%d').date()
    m = Milestone.objects.get_or_create(project=project, deadline=date)[0]
    if issue_id:
        POST_copy[issue_id + '-milestone'] = m.pk
    else:
        POST_copy['milestone'] = m.pk
    return POST_copy


class BurndownChartView(DetailView):
    model = Milestone

    def get_template_names(self):
        return ["issues/%s/burndown.html" % self.object.project.slug, "issues/burndown.html"]

    def get_context_data(self, **kwargs):
        context = super(BurndownChartView, self).get_context_data(**kwargs)
        context.update(self.object.calculate_burndown_chart(579, 150))
        return context
