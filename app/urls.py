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
    web_patterns = [
        path("", views.index, name="index"),
        path("load/", views.load, name="load"),
        path("ipfilter/", views.ipfilter, name="ipfilter"),
        path(
            "ipfilter-basic-auth/",
            views.ipfilter_basic_auth,
            name="ipfilter-basic-auth",
        ),
        path("auth/", include("authbroker_client.urls")),
        path("sso/", views.sso, name="sso"),
        path("test-api/", views.test_api, name="test-api"),
        path("noise/make", views.make_some_noise, name="noise-make"),
        # path("s3-buckets/", views.s3_buckets, name="s3-buckets")
    ]
    urlpatterns = [path("", include(web_patterns), name="index")]
