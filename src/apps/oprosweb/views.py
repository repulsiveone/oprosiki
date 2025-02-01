import string
import secrets
from itertools import islice

from smtplib import SMTPRecipientsRefused
from django.conf import settings
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from .models import CustomUser, Survey, SurveyQA
from django.db.models import F
from django.contrib import messages
from django.http import JsonResponse
from .forms import SignUpForm, SignInForm
from django.core.mail import send_mail
from django.template.loader import render_to_string


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
                        'test', 
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


#TODO не отображаются ошибки с формы
def signin(request):
    if request.user.is_authenticated:
        return redirect('/homepage')
    else:
        if request.method == "POST":
            form = SignInForm(request, request.POST)
            if form.is_valid() and form.clean():
                email = form.cleaned_data['username']
                user = CustomUser.objects.get(email=email)
                remember_me = request.POST.get('remember-me')

                if not remember_me:
                    request.session.set_expiry(0)
                    request.session.modified = True
                if user is not None:
                    login(request, user)
                    return redirect('/homepage')
                
        else:
            form = SignInForm()

    return render(request, 'app/sign_in.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('/signin')


def generate_confirmation_code(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))


def homepage(request):
    print(request.user)
    surveys = Survey.objects.all().order_by('-votes')[:4]

    if request.method == "POST":
        if request.POST.get('create-survey'):
            return redirect('/create_survey')
        if request.POST.get('list-survey'):
            return redirect('/surveys')

    return render(request, 'app/homepage.html', {'surveys': surveys})


def surveys(request):
    search = request.GET.get('search-input')
    print(search)
    if search:
        surveys = Survey.objects.filter(theme__icontains=search)
    else:
        surveys = Survey.objects.all()

    if request.method == "POST":
        pass

    return render(request, 'app/surveys-list.html', {'surveys': surveys})


def survey(request, id):
    survey = Survey.objects.get(id=id)
    questions = survey.surveyQA.all()

    if request.method == "POST":
        form_data = request.POST.dict()
        for dataVal in list(form_data):
            if 'question' in dataVal:
                question_id = dataVal.split(':')[1]
                SurveyQA.objects.filter(id=question_id).update(answer_counter=F('answer_counter')+1)
                survey.update(votes=F('votes')+1)

    return render(request, 'app/survey.html', {'survey': survey, 'questions': questions})


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

            for value in islice(form_data.values(), 3, None):
                if value != '':
                    question = SurveyQA.objects.create(
                        question=value,
                        survey=survey
                    )
            return redirect('/homepage')

    return render(request, 'app/create_survey.html')
