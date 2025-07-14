from django.contrib import messages
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.encoding import force_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode, url_has_allowed_host_and_scheme
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.backends import ModelBackend

from testria import settings
from users.forms import RegisterUserForm, LoginUserForm, UserProfileForm, UserPasswordChangeForm
from users.tasks import send_confirmation_email_task


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


def logout_view(request):
    logout(request)
    return redirect('users:login')


class UserProfileView(LoginRequiredMixin, UpdateView):
    model = get_user_model()
    form_class = UserProfileForm
    template_name = 'users/profile.html'
    extra_context = {'default_user_image': settings.DEFAULT_USER_IMAGE}

    def get_success_url(self):
        return reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        return self.request.user


class UserPasswordChangeView(PasswordChangeView):
    form_class = UserPasswordChangeForm
    template_name = 'users/password_change_form.html'
    success_url = reverse_lazy('users:password_change_done')


def verify_email_view(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist, DjangoUnicodeDecodeError):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_verified = True
        user.save()
        messages.success(request, 'Your account has been verified successfully')
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('users:home')

    else:
        messages.error(request, 'The confirmation link is invalid or has expired')
        return redirect('users:login')


@login_required
def resend_verification_email_view(request):
    next_url = request.GET.get('next')
    if next_url and \
            not url_has_allowed_host_and_scheme(next_url,
                                                allowed_hosts=request.get_host,
                                                require_https=request.is_secure):
        next_url = None

    if not next_url:
        next_url = reverse_lazy('users:profile')

    if not request.user.is_verified:
        send_confirmation_email_task.delay(request.user.pk)
        messages.info(request, 'Verification email has been sent to your email address')
    else:
        messages.success(request, 'Your email is already verified')

    return redirect(next_url)