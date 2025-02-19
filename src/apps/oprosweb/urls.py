from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('homepage/', views.homepage, name='homepage'),
    path('create_survey/', views.create_survey, name='create_survey'),
    path('survey/<int:id>', views.survey, name='survey_detail'),
    path('surveys/', views.surveys, name='surveys'),

    #user
    path('userpage/', views.userpage, name='userpage'),
    path('userpage/change_password/<int:user_id>/', views.change_password, name='change_password'),

    #auth
    path('signup/', views.signup, name='signup'),
    path('confirm_email/', views.confirm_email_page, name='confirm_email'),
    path('signin/', views.signin, name='signin'),
    path('logout/', views.logout_view, name='logout'),
    path('secure-logout/<str:signed_user_id>/', views.secure_logout, name='secure_logout'),

    #ajax
    path('get_survey_info/<int:id>', views.check_survey_info, name='check_survey_info'),
]
