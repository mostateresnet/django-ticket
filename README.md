django-ticket
=============

An issue tracker built with Django.

Downloading
-----------
```sh
pip install https://github.com/mostateresnet/django-ticket/zipball/master
```

Setup
-----
*Install requirements:*
```sh
pip install -r https://raw.github.com/mostateresnet/django-ticket/master/requirements.txt
```
*Make a new django project:*
```sh
django-admin startproject myproject
```
*Install the app:*  
In `settings.py`, under `INSTALLED_APPS = (` add the lines:
```python
'django.contrib.admin',
'issues',
```

*Set up the urls:*  
In `urls.py`, at the top, add the lines:
```python
from django.contrib import admin
admin.autodiscover()
```
In `urls.py`, under `urlpatterns = patterns('',`, add the lines:
```python
url(r'^admin/', include(admin.site.urls)),
url(r'^', include('issues.urls')),
```

*Configure your database:*  
In `settings.py` configure where it says `DATABASES = {`  
Next, run:  
```sh
python manage.py syncdb #and follow instructions
python manage.py runserver
```
In a browser go to `http://127.0.0.1:8000/admin`.
