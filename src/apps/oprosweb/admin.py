from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Survey, SurveyQA, TagsNames, SurveyTags, UserVotedSurveys


class CustomUserAdmin(UserAdmin):
    model = CustomUser



admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Survey)
admin.site.register(SurveyQA)
admin.site.register(TagsNames)
admin.site.register(SurveyTags)