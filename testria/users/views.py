from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView

from users.forms import RegisterUserForm, LoginUserForm


class RegisterUserView(CreateView):
    form_class = RegisterUserForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')


def index(request):
    return render(request, 'users/home.html')

class LoginUserView(LoginView):
    form_class = LoginUserForm
    template_name = 'users/login.html'

    def get_success_url(self):
        return reverse_lazy('users:home')

class LogoutUserView(LogoutView):
    next_page = reverse_lazy('users:login')


