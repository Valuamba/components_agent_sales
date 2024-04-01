from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from utils import send_message_to_telegram_group
from .models import Deal, Message


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
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponseNotAllowed
from django.contrib import messages
from django.urls import reverse
from .models import Deal, Message
from django.contrib.admin.views.decorators import staff_member_required
import requests


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

            print(deal)

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


@staff_member_required
def submit_message(request):
    # Ensure this view handles POST requests only
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    deal_id = request.POST.get('deal_id')
    message_text = request.POST.get('message')
    from_sender = 'manager'  # Adjust based on your logic or current user role

    print(f'Deal ID: {deal_id}')

    # Retrieve the deal, ensuring it exists
    deal = get_object_or_404(Deal, pk=deal_id)

    # Create and save the new message associated with the deal
    Message.objects.create(
        deal=deal,
        message=message_text,
        from_sender=from_sender,
    )
    send_message_to_telegram_group(message_text, deal_id)

    messages.success(request, 'Message sent successfully.')

    # Redirect back to the deal change form
    return redirect(reverse('admin:chat_deal_change', args=[deal_id]))


@csrf_exempt
def assistant_message_create(request):
    if request.method == "POST":
        deal_id = request.POST.get('deal_id')
        from_sender = request.POST.get('from_sender')

        # deal = Deal.objects.get(pk=deal_id)  # You might want to add error handling here
        # Message.objects.create(
        #     deal=deal,
        #     message=message_text,
        #     from_sender=from_sender,
        # )

    #     return JsonResponse({"status": "success", "message": message_text})
    # return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)

        url = 'http://localhost:8000/v1/agent/handle_messages/list'  # Update `/target-endpoint/` as needed

        messages = Message.objects.filter(deal_id=deal_id).exclude(from_sender='assistant').order_by('-sent_at')
        message_texts = [message.message for message in messages]

        payload = {
            "deal_id": deal_id,
            "messages": message_texts
        }

        # Specify headers, including 'Content-Type' as 'application/json'
        headers = {
            'Content-Type': 'application/json'
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            data = response.json()

            print(data)

            logs = data.get('logs', [])

            for log_entry in logs:
                from_sender = 'assistant'  # Example sender, adjust as needed

                # If deal_id is provided, find or create the corresponding deal
                if deal_id:
                    deal, created = Deal.objects.get_or_create(pk=deal_id)
                else:
                    deal = None  # Or handle as needed

                # Create a new Message for each log entry
                Message.objects.create(
                    deal=deal,
                    message=log_entry.get('log', ''),
                    from_sender=from_sender,
                    task_id=log_entry.get('task_id', None)
                )

            # Check if the request was successful
            if response.status_code == 200:
                # Process successful response
                return redirect(reverse('admin:chat_deal_change', args=[deal_id]))
            else:
                # Handle request errors
                return JsonResponse(
                    {"status": "error", "message": "Request failed with status code " + str(response.status_code)})
        except requests.exceptions.RequestException as e:
            # Handle exceptions like timeouts or connection errors
            return JsonResponse({"status": "error", "message": str(e)})

    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)