import os

from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
]

if os.getenv("IS_API"):
    urlpatterns = [
        path('', views.api, name='api')
    ]
