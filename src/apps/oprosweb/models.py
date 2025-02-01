from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=30, unique=False)
    last_name = None
    first_name = None
    last_login = None
    date_joined = None
    email = models.EmailField(max_length=60, unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',
    blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )

    def __str__(self):
        return self.username


class Survey(models.Model):
    id = models.AutoField(primary_key=True)
    theme = models.CharField(max_length=40)
    theme_description = models.CharField(max_length=100)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='survey')
    votes = models.IntegerField(default=0)


class SurveyQA(models.Model):
    id = models.AutoField(primary_key=True)
    question = models.CharField(max_length=40)
    answer_counter = models.IntegerField(default=0)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='surveyQA')


# class UserSurvey(models.Model):
#     id = models.AutoField(primary_key=True)

