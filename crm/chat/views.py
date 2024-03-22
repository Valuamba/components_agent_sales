from django.shortcuts import render, redirect


def chat_room(request, room_name):
    return render(request, 'chat/chat_room.html', {
        'room_name': room_name
    })


def admin_chat_redirect(request):
    return redirect('/chat/admin_room/')  # Adjust the URL as needed