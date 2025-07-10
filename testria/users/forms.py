from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


class RegisterUserForm(UserCreationForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput())
    password2 = forms.CharField(label='Repeat password', widget=forms.PasswordInput())

    class Meta:
        model=get_user_model()
        fields=['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def clean_email(self):
        email=self.cleaned_data['email']
        if get_user_model().objects.filter(email=email).exists():
            raise forms.ValidationError('This email already exists')
        else:
            return email

class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Email/username')

    class Meta:
        model=get_user_model()