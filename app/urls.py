from django.conf import settings
from django.urls import include
from django.urls import path

from . import views

if settings.IS_API:
    api_patterns = [
        path("", views.api, name="api"),
        path("test-web/", views.test_web, name="test-web"),
    ]
    urlpatterns = [path("", include(api_patterns), name="api")]
else:
    urlpatterns = [path("", views.index, name="index")]
