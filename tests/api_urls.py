# Django only loads urls once during tests, so it's not possible to toggle between API and web urls using `@override_settings(IS_API=True)`
# Instead we use `@override_settings(ROOT_URLCONF='tests.api_urls')` to point at this file

from django.urls import include
from django.urls import path

from app import views

api_patterns = [
    path("", views.api, name="api"),
    path("test-web/", views.test_web, name="test-web"),
]
urlpatterns = [path("", include(api_patterns), name="api")]
