from django.shortcuts import render, redirect


def chat_room(request, room_name):
    return render(request, 'chat/chat_room.html', {
        'room_name': room_name
    })


def admin_chat_redirect(request):
    return redirect('/chat/admin_room/')  # Adjust the URL as needed


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Deal, Message
from .serializers import MessageSerializer


class MessageAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data

            # Handle the creation or update of Deal and Message here
            deal, created = Deal.objects.get_or_create(
                deal_id=data['thread_id'],
                defaults={
                    'subject': data['topic_name'],
                    'customer': data['sender']
                }
            )

            message = Message.objects.create(
                deal=deal,
                message=data['message'],
                from_sender='customer'  # Assuming 'customer' is a valid sender; adjust if needed
            )

            # Assuming you want to return the created message or some confirmation
            return_data = {
                "deal_id": deal.deal_id,
                "message": message.message,
                "subject": deal.subject,
                "customer": deal.customer
            }
            return Response(return_data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
