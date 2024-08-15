from django.conf import settings
from django.urls import path, include

from . import views

if settings.IS_API:
    api_patterns = [
        path('', views.api, name='api'), 
        path('test-web/', views.test_web, name='test-web'),  
    ]
    urlpatterns = [
        path('', include(api_patterns), name='api')
    ]
else:
    web_patterns = [
        path('', views.index, name='index'),
        path('ipfilter/', views.ipfilter, name='ipfilter'),
        path('ipfilter-basic-auth/', views.ipfilter_basic_auth, name="ipfilter-basic-auth"),
    ]
    urlpatterns = [
        path('', include(web_patterns), name='index')
    ]
