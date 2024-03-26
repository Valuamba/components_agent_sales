from django.contrib import admin
from .models import Deal, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 1  # How many extra forms to show


class DealAdmin(admin.ModelAdmin):
    list_display = ('deal_id', 'subject', 'customer')  # Fields to display in the admin list view
    search_fields = ('deal_id', 'subject', 'customer')  # Fields to search by in the admin list view
    # inlines = [MessageInline]  # Include MessageInline to manage messages within a deal


class MessageAdmin(admin.ModelAdmin):
    list_display = ('message', 'sent_at', 'from_sender')  # Fields to display in the admin list view
    list_filter = ('sent_at', 'from_sender')  # Fields to filter by in the admin list view
    search_fields = ('message',)  # Fields to search by in the admin list view


admin.site.register(Deal, DealAdmin)
admin.site.register(Message, MessageAdmin)