# views.py
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import AndroidApp, UserProfile, Task
from .serializers import UserSerializer, AndroidAppSerializer, UserProfileSerializer, TaskSerializer
from django.shortcuts import get_object_or_404

@api_view(['POST'])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        user.set_password(request.data['password'])
        user.save()
        UserProfile.objects.create(user=user)
        token = Token.objects.create(user=user)
        return Response({'token': token.key, 'user': serializer.data})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login(request):
    user = User.objects.filter(username=request.data['username']).first()
    if user and user.check_password(request.data['password']):
        token, _ = Token.objects.get_or_create(user=user)
        serializer = UserSerializer(user)
        return Response({'token': token.key, 'user': serializer.data})
    return Response("Invalid credentials", status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAdminUser])
def add_android_app(request):
    serializer = AndroidAppSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    profile = UserProfile.objects.get(user=request.user)
    serializer = UserProfileSerializer(profile)
    return Response(serializer.data)

@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_android_apps(request):
    apps = AndroidApp.objects.all()
    serializer = AndroidAppSerializer(apps, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def upload_screenshot(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    
    if 'screenshot' in request.FILES:
        task.screenshot = request.FILES['screenshot']
        
        if not task.completed:
            task.completed = True
            task.save()
            
            profile = UserProfile.objects.get(user=request.user)
            profile.tasksCompleted += 1
            profile.save()
        
        task_serializer = TaskSerializer(task)
        profile_serializer = UserProfileSerializer(profile)
        
        return Response({
            "message": "Screenshot uploaded and task completed",
            "task": task_serializer.data,
            "user_profile": profile_serializer.data
        }, status=status.HTTP_200_OK)
    
    return Response({"error": "No screenshot provided"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_user_tasks(request):
    tasks = Task.objects.filter(user=request.user)
    task_serializer = TaskSerializer(tasks, many=True)
    
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    profile_serializer = UserProfileSerializer(user_profile)
    
    response_data = {
        "user_profile": profile_serializer.data,
        "tasks": task_serializer.data
    }
    
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def download_app(request):
    app_id = request.data.get('app_id')
    if not app_id:
        return Response({"error": "app_id is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    app = get_object_or_404(AndroidApp, id=app_id)
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Check if the user has already downloaded this app
    existing_task = Task.objects.filter(user=request.user, app=app).first()
    if existing_task:
        return Response({"error": "You have already downloaded this app"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Create a new task
    Task.objects.create(user=request.user, app=app, completed=False)
    
    # Update user profile
    user_profile.points_earned += app.points
    user_profile.save()
    
    serializer = UserProfileSerializer(user_profile)
    return Response({
        "message": f"Successfully downloaded {app.name}",
        "points_earned": app.points,
        "total_points": user_profile.points_earned,
        "user_profile": serializer.data
    }, status=status.HTTP_200_OK)