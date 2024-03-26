from django.db import models
from django.core.validators import EmailValidator


class Deal(models.Model):
    deal_id = models.CharField(max_length=50, unique=True)  # Unique identifier for the deal
    subject = models.CharField(max_length=255)  # Subject or title of the deal
    customer = models.CharField(max_length=100)  # Customer's email address

    def __str__(self):
        return f"Deal {self.deal_id} - {self.subject}"


class Message(models.Model):
    # Choices for the sender of the message
    SENDER_CHOICES = [
        ('manager', 'Manager'),
        ('customer', 'Customer'),
        ('assistant', 'Assistant'),
    ]

    deal = models.ForeignKey(Deal, on_delete=models.CASCADE, related_name='messages')  # Associates messages with a deal

    message = models.TextField()  # The message content
    sent_at = models.DateTimeField(auto_now_add=True)  # The timestamp when the message was sent
    from_sender = models.CharField(max_length=10, choices=SENDER_CHOICES)  # The sender of the message

    def __str__(self):
        return f"Message from {self.from_sender} at {self.sent_at}"