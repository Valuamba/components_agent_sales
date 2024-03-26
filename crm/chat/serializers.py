from rest_framework import serializers


class MessageSerializer(serializers.Serializer):
    thread_id = serializers.CharField(max_length=50)
    message = serializers.CharField()
    topic_name = serializers.CharField(max_length=255)
    sender = serializers.CharField(max_length=255)
