from django.contrib import messages
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode, url_has_allowed_host_and_scheme
from django.views.generic import CreateView, UpdateView, DetailView

from testria import settings
from users.forms import RegisterUserForm, LoginUserForm, UserProfileForm, UserPasswordChangeForm

from .custom_user_errors import *
from .user_services import UserServices
from .utils import SubscriptionsListMixin


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

class OtherUserView(LoginRequiredMixin, DetailView):
    model = get_user_model()
    template_name = 'users/other_user_profile.html'
    context_object_name = 'user'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        if self.request.user==self.object:
            return redirect('users:profile')
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        context['default_user_image']=settings.DEFAULT_USER_IMAGE
        if self.request.user!=self.get_object():
            context['is_following']=self.request.user.is_following(self.get_object())
        else:
            context['is_following']=False
        return context

@login_required
def follow_view(request, username):
    try:
        UserServices.follow_on(request, username)
        messages.success(request, f"You're started following on {username}")
        return redirect('users:view_profile', username)
    except FollowOnYourselfError as e:
        messages.error(request, e)
        return redirect('users:profile')
    except AlreadyFollowedOnUserError as e:
        messages.info(request, e)
        return redirect('users:profile')


@login_required
def unfollow_view(request, username):
    UserServices.unfollow_on(request, username)
    return redirect('users:view_profile', username)


def verify_email_view(request, uidb64, token):

    try:
        user=UserServices.verify_email(uidb64, token)
        messages.success(request, 'Your account has been verified successfully')
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('users:home')
    except ConfirmationLinkError as e:
        messages.error(request, e)
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

    if UserServices.resend_verification_email(request):
        messages.info(request, 'Verification email has been sent to your email address')
    else:
        messages.success(request, 'Your email is already verified')

    return redirect(next_url)

class ListFollowingView(SubscriptionsListMixin):
    template_name = 'users/following_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['following'] = self.request.user.following.all()
        return context

class ListFollowersView(SubscriptionsListMixin):
    template_name = 'users/followers_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['followers'] = self.request.user.followers.all()
        return context


