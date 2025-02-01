from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.oprosweb.urls')),
    path('homepage/', include('apps.oprosweb.urls')),
    path('create_survey/', include('apps.oprosweb.urls')),
    path('survey/<int:id>', include('apps.oprosweb.urls')),
    path('surveys/', include('apps.oprosweb.urls')),

    #auth
    path('signup/', include('apps.oprosweb.urls')),
    path('confirm_email/', include('apps.oprosweb.urls')),
    path('signin/', include('apps.oprosweb.urls')),
    path('logout/', include('apps.oprosweb.urls')),

    #ajax
    path('get_survey_info/<int:id>', include('apps.oprosweb.urls')),
]
