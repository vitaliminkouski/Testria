from django.contrib.auth import get_user_model
from rest_framework import serializers

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
            'second_name': {'required': False},
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
