import os

from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/', views.api, name="api")
]

if os.getenv("IS_API"):
    urlpatterns = [
        path('', views.api, name='api')
    ]
