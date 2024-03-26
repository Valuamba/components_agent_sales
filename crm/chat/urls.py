from . import views
from .views import admin_chat_redirect, submit_message, assistant_message_create
from django.urls import path
from .views import MessageAPIView


urlpatterns = [
    path('api/message/', MessageAPIView.as_view(), name='message_api'),
    path('submit_message/', submit_message, name='your_message_submission_view'),
    path('assistant-message-create/', assistant_message_create, name='assistant_message_create'),
    # path('chat/<str:room_name>/', views.chat_room, name='chat_room'),
    # path('admin/chat/', admin_chat_redirect, name='admin_chat_redirect')
]
