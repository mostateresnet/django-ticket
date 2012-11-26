import urllib, hashlib
from django import template

register = template.Library()

@register.filter
def gravatar(email, size=32):
    default = "mm"
    url = "http://www.gravatar.com/avatar.php?"
    url += urllib.urlencode({
        'gravatar_id': hashlib.md5(email).hexdigest(),
        'default': default,
        'size': str(size)
    })
    return url

