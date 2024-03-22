from django.urls import path
from . import views
from .views import admin_chat_redirect

urlpatterns = [
    path('chat/<str:room_name>/', views.chat_room, name='chat_room'),
    path('admin/chat/', admin_chat_redirect, name='admin_chat_redirect')
]
