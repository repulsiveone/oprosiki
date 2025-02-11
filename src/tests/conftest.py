import pytest
from django.test import RequestFactory, Client
from apps.oprosweb.models import CustomUser, Survey, SurveyQA, UserVotedSurveys

@pytest.fixture
def user():
    return CustomUser.objects.create_user(
        username='xpfxz',
        email='xpfxz@bk.ru',
        password='qweqweqwe',
    )

@pytest.fixture
def survey(user):
    return Survey.objects.create(
        user=user,
        theme='test_theme',
        theme_description ='test_description'
    )

@pytest.fixture
def survey_qa(survey):
    return SurveyQA.objects.create(
        survey=survey,
        question='test_question'
    )

@pytest.fixture
def user_voted(user, survey_qa, survey):
    return UserVotedSurveys.objects.create(
        user = user,
        survey_answer = survey_qa,
        survey=survey
    )

@pytest.fixture
def client():
    return Client()

@pytest.fixture
def factory():
    return RequestFactory()