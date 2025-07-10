from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm


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

class UserProfileForm(forms.ModelForm):
    username=forms.CharField(disabled=True)
    email=forms.CharField(disabled=True)
    class Meta:
        model=get_user_model()
        fields=['photo', 'username', 'first_name', 'last_name', 'email',  'bio', ]

class UserPasswordChangeForm(PasswordChangeForm):
    new_password1 = forms.CharField(label='New password')
    new_password2 = forms.CharField(label='Repeat new password')