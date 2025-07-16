from django.contrib.auth import get_user_model
from rest_framework import generics

from users.api.serializers import UserRegisterSerializer


class UserRegisterAPIView(generics.CreateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserRegisterSerializer