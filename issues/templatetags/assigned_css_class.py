import datetime
from django import template

register = template.Library()
        
@register.simple_tag(name="assigned_css_class")
def simple_assigned_css_class(assigned_to, user, status):
    if (assigned_to):
        if assigned_to == user and status == 'IP':
            css_class='in-progress'
        elif assigned_to == user and status == 'AS':
            css_class='assigned'
        else:
            css_class='unassigned'
    else:
        css_class='unassigned'
    return css_class
