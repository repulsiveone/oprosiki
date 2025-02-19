from itertools import islice
import pickle
from smtplib import SMTPRecipientsRefused
from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.hashers import check_password
from django.shortcuts import render, redirect
from .models import CustomUser, Survey, SurveyQA, UserVotedSurveys, TagsNames, SurveyTags
from django.db.models import F
from django.contrib import messages
from django.http import JsonResponse
from .forms import SignUpForm, CustomSignInForm
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.core.signing import Signer, BadSignature
from .utils import generate_confirmation_code, generate_secure_link
from django.contrib.sessions.backends.base import SessionBase
from redis import Redis
from config.celery import update_user_tag, get_user_tag
from django.core.cache import cache


def signup(request):
    if request.user.is_authenticated:
        return redirect('/homepage')
    else:
        if request.method == 'POST':
            form = SignUpForm(request.POST)
            if form.is_valid():
                confirmation_code = generate_confirmation_code()
                print(confirmation_code)
                username = form.cleaned_data['username']
                request.session['confirmation_code'] = confirmation_code
                request.session['username'] = form.cleaned_data['username']
                request.session['email'] = form.cleaned_data['email']
                request.session['password'] = form.cleaned_data['password1']
                
                try:
                    send_mail(
                        'Код подтверждения', 
                        'test_message',
                        settings.EMAIL_HOST_USER,
                        [request.session['email']],
                        fail_silently=False,

                        html_message=render_to_string(
                            'app/email-template.html',
                            {
                                'confirmation_code': confirmation_code, 
                                'username': username
                            }))

                    return redirect('confirm_email/')

                except SMTPRecipientsRefused:
                    messages.info(request, 
                                "Похоже, что почта, которую вы указали, не существует."\
                                "Пожалуйста, проверьте правильность адреса и повторите попытку.")
                
        else:
            form = SignUpForm()
    
    return render(request, 'app/sign_up.html', {'form': form})


def confirm_email_page(request):
    confirmation_code = request.session['confirmation_code']
    username= request.session['username']
    email = request.session['email']
    password = request.session['password']

    if request.method == "POST":

        if request.POST.get('confirmation-user-code') == confirmation_code:
            user = CustomUser.objects.create_user(username, email, password)
            login(request, user)
            
            del request.session['username']
            del request.session['email']
            del request.session['password']
            del request.session['confirmation_code']

            return redirect('/homepage')

    return render(request, 'app/password-veirfy-page.html')


def signin(request):
    if request.user.is_authenticated:
        return redirect('/homepage')
    else:
        if request.method == "POST":
            form = CustomSignInForm(request.POST)
            if form.is_valid():
                email = form.cleaned_data['email']
                user = CustomUser.objects.get(email=email)
                remember_me = request.POST.get('remember-me')

                if not remember_me:
                    request.session.set_expiry(0)
                    request.session.modified = True
                if user is not None:
                    login(request, user)
                    
                    try:
                        send_mail(
                            'Вход в аккаунт', 
                            f'Вы вошли в аккаунт. Если это были не вы, нажмите на ссылку: {generate_secure_link(user.id)}',
                            settings.EMAIL_HOST_USER,
                            [email],
                            fail_silently=False,
                        )
                        return redirect('/homepage')

                    except SMTPRecipientsRefused:
                        messages.info(request, 
                                    "Похоже, что почта, которую вы указали, не существует."\
                                    "Пожалуйста, проверьте правильность адреса и повторите попытку.")
                    return redirect('/homepage')
                
        else:
            form = CustomSignInForm(request.POST)

    return render(request, 'app/sign_in.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('/signin')


def secure_logout(request, signed_user_id):
    signer = Signer()
    try:
        user_id = signer.unsign(signed_user_id)
        user = CustomUser.objects.get(id=user_id)

        # Отладочный вывод: Проверка подключения к Redis
        redis_client = Redis(host='127.0.0.1', port=6379, db=1)
        try:
            redis_client.ping()
        except Exception as e:
            return render(request, 'error.html', {'error': f'Ошибка подключения к Redis: {e}'})
        
        session_keys_to_delete = []
    
        patterns_to_try = [
            b'*:django.contrib.sessions.*',
            b'*:*django.contrib.sessions.*',
            b'*:*',
        ]
        #получаем информацию о сессиях пользователя, pickle используется для преобразования байтов в объект
        for pattern in patterns_to_try:
            try:
                for key in redis_client.scan_iter(pattern):
                    session_data = redis_client.get(key)
                    try:
                        decoded_data = session_data.decode('utf-8')
                    except UnicodeDecodeError:
                        decoded_data = pickle.loads(session_data)
                    if '_auth_user_id' in decoded_data and decoded_data['_auth_user_id'] == str(user.id):
                        session_keys_to_delete.append(key.decode('utf-8'))    
  
            except Exception as e:
                print(f"Ошибка при сканировании ключей сессий: {e}")
        
        if session_keys_to_delete:
            redis_client.delete(*session_keys_to_delete)

        logout(request)
        return redirect('/signin')

    except BadSignature:
        return render(request, 'error.html', {'error': 'Неверная ссылка'})
    except CustomUser.DoesNotExist:
        return render(request, 'error.html', {'error': 'Пользователь не найден'})
    except Exception as e:
        print(f"Произошла непредвиденная ошибка: {e}")
        return render(request, 'error.html', {'error': 'Произошла ошибка при выходе из системы'})
 

def homepage(request):
    print(request.user)
    surveys = Survey.objects.all().order_by('-votes')[:4]

    if request.method == "POST":
        if request.POST.get('create-survey'):
            return redirect('/create_survey')
        if request.POST.get('list-survey'):
            return redirect('/surveys')

    return render(request, 'app/homepage.html', {'surveys': surveys})


def userpage(request):
    user_id = request.user.id
    user_info = CustomUser.objects.get(id=user_id)
    user_surveys = Survey.objects.filter(user=user_info)
    
    if request.method == "POST":
        if request.POST.get('change-password-button'):
            return redirect(f'/userpage/change_password/{user_id}')
        if request.POST.get('username-change'):
            new_username = request.POST.get('text-input')
            user_info.username = new_username
            user_info.save()
            return redirect('/userpage')
    return render(request, 'app/userpage.html', {'user_info': user_info, 'user_surveys': user_surveys})


# TODO сделать фронтенд
def change_password(request, user_id):
    current_user_id = request.user.id
    user = CustomUser.objects.get(id=user_id)
    if user.id == current_user_id:
        if request.method == "POST":
            old_password = request.POST.get('old-password-input')
            new_password = request.POST.get('new-password-input')
            if user.check_password(old_password):
                user.set_password(new_password)
                user.save()
                return redirect('/userpage')
            return redirect(f'/userpage/change_password/{current_user_id}')
        return render(request, 'app/change_password.html')
    return redirect('/userpage')


def surveys(request):
    search = request.GET.get('search-input')
    
    if search: 
        surveys = Survey.objects.filter(theme__icontains=search)
    else:
        surveys = Survey.objects.all()

    if request.method == "POST":
        cached_surveys = cache.get(f'user:{request.user.id}:surveys')

        if cached_surveys:
            surveys = cached_surveys

    return render(request, 'app/surveys-list.html', {'surveys': surveys})


def survey(request, id):
    survey = Survey.objects.get(id=id)
    questions = survey.surveyQA.all()
    user_vote = UserVotedSurveys.objects.filter(user=request.user, survey=survey)
    survey_tags = SurveyTags.objects.filter(survey=survey)
    get_user_tag(request.user.id)
    if request.method == "POST":
        if request.user.is_authenticated and not user_vote:
            form_data = request.POST.dict()
            print(form_data)
            for dataVal in list(form_data):
                if 'question' in dataVal:
                    question_id = dataVal.split(':')[1]
                    answer = SurveyQA.objects.get(id=question_id)
                    #обновление сколько раз выбран данный ответ
                    SurveyQA.objects.filter(id=question_id).update(answer_counter=F('answer_counter')+1)
                    # обновление сколько людей проголосовало в опросе
                    Survey.objects.filter(id=id).update(votes=F('votes')+1)
                    # добавление связи пользователя и ответа
                    UserVotedSurveys.objects.create(user=request.user, survey_answer=answer, survey=survey)
            
            list_of_tags = []
            for i in survey_tags:
                list_of_tags.append(i.tag.tag_name)
            update_user_tag.delay(request.user.id, list_of_tags)
            get_user_tag.delay(request.user.id)

        else:
            return redirect('/signin')

    return render(request, 'app/survey.html', {'survey': survey, 'questions': questions, 'survey_tags': survey_tags})


def check_survey_info(request, id):
    questionsList = []
    count_answers = []

    survey = Survey.objects.get(id=id)
    survquestions = survey.surveyQA.all()
    for i in survquestions:
        questionsList.append(i.question)
        count_answers.append(i.answer_counter)

    return JsonResponse(data={'questionsList': questionsList, 'count_answers': count_answers})


def create_survey(request):
    if request.user.is_authenticated:
        tags = TagsNames.objects.all()
        if request.method == "POST":
            user = CustomUser.objects.get(id=1)
            form_data = request.POST.dict()
            if not form_data.get('theme') or not form_data.get('theme-description'):
                messages.info(request, "*Данное поле не может быть пустым")
            else:
                survey = Survey.objects.create(
                    theme=form_data.get('theme'),
                    theme_description=form_data.get('theme-description'),
                    user=user
                )

                for dataVal in list(form_data):
                    if 'tag:' in dataVal:
                        val = dataVal.split(':')[1]
                        if TagsNames.objects.filter(tag_name=val):
                            tag_name = TagsNames.objects.get(tag_name=val)
                        else:
                            tag_name = TagsNames.objects.create(tag_name=val)

                        SurveyTags.objects.create(survey=survey, tag=tag_name)

                # for value in islice(form_data.values(), 3, None):
                for key in form_data:
                    if 'option' in key and form_data[key] != '':
                        question = SurveyQA.objects.create(
                            question=form_data[key],
                            survey=survey
                        )

                return redirect('/homepage')

        return render(request, 'app/create_survey.html', {'survey_tags': tags})
    else:
        return redirect('/signin')
