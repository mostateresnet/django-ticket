from django import template

register = template.Library()


@register.filter
def has_new_notes(issue, user):
    return issue.has_new_notes(user)
