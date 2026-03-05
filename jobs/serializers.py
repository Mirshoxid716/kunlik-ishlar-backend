from rest_framework import serializers
from .models import Job, Worker, Application
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'is_superuser', 'is_staff']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            is_staff=True,
            is_superuser=validated_data.get('is_superuser', False)
        )
        return user

class WorkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Worker
        fields = '__all__'

class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = '__all__'

class ApplicationSerializer(serializers.ModelSerializer):
    worker_details = WorkerSerializer(source='worker', read_only=True)
    job_details = JobSerializer(source='job', read_only=True)

    class Meta:
        model = Application
        fields = '__all__'
