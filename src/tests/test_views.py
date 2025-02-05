import pytest
from django.urls import reverse
from apps.oprosweb.models import CustomUser, Survey, SurveyQA
from apps.oprosweb.views import survey as surv

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