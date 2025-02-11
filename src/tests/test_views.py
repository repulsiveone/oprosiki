import pytest
from django.urls import reverse
from apps.oprosweb.models import CustomUser, Survey, SurveyQA, UserVotedSurveys
from apps.oprosweb.views import survey as surv
from apps.oprosweb.views import change_password

@pytest.mark.django_db
def test_survey_view_post(factory, user, survey, survey_qa):
    url = reverse('survey_detail', args=[survey.id])
    form_data = {
        f'question:{survey_qa.id}': 'Test Answer'
    }
    request = factory.post(url, data=form_data)
    request.user = user

    response = surv(request, id=survey.id)

    survey_qa.refresh_from_db()
    survey.refresh_from_db()
    
    assert survey_qa.answer_counter == 1
    assert survey.votes == 1

    user_voted = UserVotedSurveys.objects.get(user=user, survey=survey)
    assert user_voted.survey_answer == survey_qa

@pytest.mark.django_db
def test_change_password(client, user):
    client.force_login(user)
    url = reverse('change_password', args=[user.id])
    form_data = {
        'old-password-input': 'qweqweqwe',
        'new-password-input': 'qwertyqwerty',
    }
    response = client.post(url, data=form_data)

    user.refresh_from_db()
    assert user.check_password('qwertyqwerty') == True
    assert user.check_password('qweqweqwe') == False