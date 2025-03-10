from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ValidationError


class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Enter the email'})
        )
    
    username = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'placeholder': 'Enter the username'})
    )

    password1 = forms.CharField(
        max_length=40,
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter the password'})
    )

    password2 = forms.CharField(
        max_length=40,
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm the password'})
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')
    

class CustomSignInForm(forms.Form):
    email = forms.EmailField(
        widget=forms.TextInput(attrs={'placeholder': 'Enter the email'})
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'password'})
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            self.add_error('email', 'Неправильный адрес электронной почты')
            return

        if not user.check_password(password):
            self.add_error('password', 'Неправильный пароль')
            return
        
        return cleaned_data

    