from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
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


@staff_member_required
def submit_message(request):
    # Ensure this view handles POST requests only
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    deal_id = request.POST.get('deal_id')
    message_text = request.POST.get('message')
    from_sender = 'manager'  # Adjust based on your logic or current user role

    # Retrieve the deal, ensuring it exists
    deal = get_object_or_404(Deal, pk=deal_id)

    # Create and save the new message associated with the deal
    Message.objects.create(
        deal=deal,
        message=message_text,
        from_sender=from_sender,
    )

    messages.success(request, 'Message sent successfully.')

    # Redirect back to the deal change form
    return redirect(reverse('admin:chat_deal_change', args=[deal_id]))


@csrf_exempt
def assistant_message_create(request):
    if request.method == "POST":
        deal_id = request.POST.get('deal_id')
        message_text = request.POST.get('message')
        from_sender = request.POST.get('from_sender')

        deal = Deal.objects.get(pk=deal_id)  # You might want to add error handling here
        Message.objects.create(
            deal=deal,
            message=message_text,
            from_sender=from_sender,
        )

        return JsonResponse({"status": "success", "message": message_text})
    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)
