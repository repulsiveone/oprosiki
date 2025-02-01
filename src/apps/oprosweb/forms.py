from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms


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


class SignInForm(AuthenticationForm):
    username = forms.EmailField(
        widget=forms.TextInput(attrs={'placeholder': 'Enter the email'})
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'password'}))

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('username')

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist: 
            self.add_error('username', 'Неправильный адрес электронной почты')
            return

        cleaned_data['email'] = user

        return cleaned_data