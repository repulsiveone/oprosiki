import pytest
from apps.oprosweb.models import Survey, CustomUser, UserVotedSurveys, SurveyQA

@pytest.mark.django_db
def test_survey_creation():
    user = CustomUser.objects.create(
        username='xpfxz',
        email='xpfxz@bk.ru'
    )
    survey = Survey.objects.create(
        theme='test_theme',
        theme_description='test_description',
        user = user
        )
    
    assert survey.theme == 'test_theme'
    assert survey.theme_description == 'test_description'
    assert survey.user == user

    user_surveys = user.survey.all()
    assert survey in user_surveys


@pytest.mark.django_db
def test_user_voted(user, survey_qa, survey):
    voted = UserVotedSurveys.objects.create(
        user = user,
        survey_answer = survey_qa,
        survey = survey
    )

    assert voted.survey_answer == survey_qa
