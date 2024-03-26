from django.db import models
from django.core.validators import EmailValidator


class AgentTask(models.Model):
    task_id = models.AutoField(primary_key=True)
    completion_cost = models.FloatField(null=True, blank=True)
    output_tokens = models.IntegerField(null=True, blank=True)
    prompt_tokens = models.IntegerField(null=True, blank=True)
    prompt = models.TextField()
    response = models.TextField(null=True, blank=True)
    agent_type = models.IntegerField()
    status = models.CharField(max_length=50)  # Adjust max_length as needed
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    deal_id = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'agent_task'


class Deal(models.Model):
    deal_id = models.CharField(max_length=50, unique=True, primary_key=True)  # Unique identifier for the deal
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