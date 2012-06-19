from issues.models import *
from django.contrib import admin

class IssueInline(admin.TabularInline):
    model = Issue
    extra = 1

class MilestoneInline(admin.TabularInline):
    model = Milestone
    extra = 0

class ProjectAdmin(admin.ModelAdmin):
    # fields = ['name', 'last_name', 'bearpass_number', 'rms_id', 'gender', 'organization', 'start_date', 'recommended_bedspace']
    prepopulated_fields = {"slug": ("name",)}
    # list_display = ['name', 'last_name', 'bearpass_number', 'rms_id', 'gender', 'organization', 'start_date', 'recommended_bedspace']
    inlines = [IssueInline, MilestoneInline]

admin.site.register(Project, ProjectAdmin)
