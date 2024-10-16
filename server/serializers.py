from rest_framework import serializers
from django.contrib.auth.models import User
from .models import AndroidApp, UserProfile, Task

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email', 'is_staff']
        extra_kwargs = {'password': {'write_only': True}}

class AndroidAppSerializer(serializers.ModelSerializer):
    class Meta:
        model = AndroidApp
        fields = '__all__'

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = '__all__'

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'