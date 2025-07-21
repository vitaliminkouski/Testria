from typing import Any

from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from prompt_toolkit.validation import ValidationError
from rest_framework import serializers

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class UserRegisterSerializer(serializers.ModelSerializer):
    password1=serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2=serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model=get_user_model()
        fields=['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        extra_kwargs={
            'username': {'required': True},
            'email': {'required': True},
            'first_name': {'required': False},
            'last_name': {'required': False},
        }

    def validate(self, data):
        if data['password1']!=data['password2']:
            raise serializers.ValidationError("Passwords isn't matched")
        return data

    def create(self, validated_data):
        user=get_user_model().objects.create_user(
            username=validated_data['username'],
            password=validated_data['password1'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
        )
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=get_user_model()
        fields=['photo', 'username', 'first_name', 'last_name', 'email',  'bio', 'is_verified']
        read_only_fields=['username', 'email', 'is_verified']

class OtherUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['photo', 'username', 'first_name', 'last_name', 'bio',]
        read_only_fields = fields

class PasswordResetRequestSerializer(serializers.Serializer):
    email=serializers.EmailField(required=True)

    def validate_email(self, value):
        if not get_user_model().objects.filter(email=value).exists():
            raise serializers.ValidationError('No user is associated with this email address')
        return value

class PasswordResetConfirmSerializer(serializers.Serializer):
    uid=serializers.CharField(required=True)
    token=serializers.CharField(required=True)
    new_password1=serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    new_password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    def validate(self, data):
        if data['new_password1']!=data['new_password2']:
            raise serializers.ValidationError("These passwords are not matched")
        try:
            uid=force_str(urlsafe_base64_decode(data['uid']))
            self.user=get_user_model().objects.get(pk=uid)
        except:
            raise serializers.ValidationError({"uid": "Invalid user id"})

        if not default_token_generator.check_token(self.user, data['token']):
            raise serializers.ValidationError({"token": "Invalid or expired token"})

        try:
            validate_password(data['new_password1'], self.user)
        except Exception as e:
            raise serializers.ValidationError({"password": list(e.messages)})

        return data

    def save(self, **kwargs):
        self.user.set_password(self.validated_data['new_password1'])
        self.user.save()
        return self.user


class EmailConfirmationSerializer(serializers.Serializer):
    uid=serializers.CharField(required=True)
    token=serializers.CharField(required=True)

class PasswordChangeSerializer(serializers.Serializer):
    old_password=serializers.CharField(write_only=True, required=True, style={"input-type": "password"})
    new_password1 = serializers.CharField(write_only=True, required=True, style={"input-type": "password"})
    new_password2 = serializers.CharField(write_only=True, required=True, style={"input-type": "password"})

    def validate_old_password(self, value):
        user=self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is not correct")
        return value

    def validate(self, data):
        if data['new_password1']!=data['new_password2']:
            raise serializers.ValidationError("New passwords are not matched")

        user=self.context['request'].user
        try:
            validate_password(data['new_password1'], user)
        except Exception as e:
            raise serializers.ValidationError({"new_password": list(e.messages)})

        return data

    def save(self, **kwargs):
        user=self.context['request'].user
        user.set_password(self.validated_data['new_password1'])
        user.save()
        return user

class SessionLoginSerializer(serializers.Serializer):
    username=serializers.CharField(required=True)
    password=serializers.CharField(write_only=True, required=True, style={'input-type': 'password'})

    def validate(self, data):
        username=data.get('username')
        password=data.get('password')


        user=authenticate(request=self.context['request'], username=username, password=password)
        if not user:
            raise serializers.ValidationError('Unable to authenticate user')

        data['user']=user
        return data

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):


    def validate(self, data):
        username_or_email=data.get('username', None)
        password=data.get('password', None)

        user=authenticate(request=self.context.get('request'), username=username_or_email,
                          password=password)
        if not user:
            raise serializers.ValidationError("Invalid authentication. Check your username/email and password")

        return super().validate(data)