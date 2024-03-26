from . import views
from .views import admin_chat_redirect
from django.urls import path
from .views import MessageAPIView


urlpatterns = [
    path('api/message/', MessageAPIView.as_view(), name='message_api'),
    # path('chat/<str:room_name>/', views.chat_room, name='chat_room'),
    # path('admin/chat/', admin_chat_redirect, name='admin_chat_redirect')
]
