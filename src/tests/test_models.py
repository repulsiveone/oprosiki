import pytest
from apps.oprosweb.models import Survey, CustomUser

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