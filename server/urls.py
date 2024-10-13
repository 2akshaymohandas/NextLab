from django.urls import re_path

from . import views

urlpatterns = [
    re_path('signup/', views.signup),
    re_path('login/', views.login),
    re_path('add_android_app/', views.add_android_app),
    re_path('get_user_profile/', views.get_user_profile),
    re_path('get_android_apps/', views.get_android_apps),
    re_path(r'^upload_screenshot/(?P<task_id>\d+)/$', views.upload_screenshot),
    re_path('download_app/', views.download_app),
    re_path('get_user_tasks/', views.get_user_tasks),
]