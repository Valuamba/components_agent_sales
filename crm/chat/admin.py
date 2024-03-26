from django.contrib import admin
from .models import Deal, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 1  # How many extra forms to show


class DealAdmin(admin.ModelAdmin):
    list_display = ('deal_id', 'subject', 'customer')  # Fields to display in the admin list view
    search_fields = ('deal_id', 'subject', 'customer')  # Fields to search by in the admin list view

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        messages = Message.objects.filter(deal_id=object_id).order_by('sent_at')
        extra_context['messages'] = messages
        return super().changeform_view(request, object_id, form_url, extra_context)


class MessageAdmin(admin.ModelAdmin):
    list_display = ('message', 'sent_at', 'from_sender')  # Fields to display in the admin list view
    list_filter = ('sent_at', 'from_sender')  # Fields to filter by in the admin list view
    search_fields = ('message',)  # Fields to search by in the admin list view


admin.site.register(Deal, DealAdmin)
admin.site.register(Message, MessageAdmin)