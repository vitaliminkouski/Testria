from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView


class SubscriptionsListMixin(LoginRequiredMixin, DetailView):
    model=get_user_model()
    slug_field = 'username'
    slug_url_kwarg = 'username'

    template_name = None
