import os

from django.conf import settings
from django.urls import path

from . import views

if settings.IS_API:
    urlpatterns = [
        path('', views.api, name='api')
    ]
else:
    urlpatterns = [
        path('', views.index, name='index')
    ]
