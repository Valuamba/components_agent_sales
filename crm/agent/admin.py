from django.contrib import admin
from .models import AgentTask
from django.utils.html import format_html
from django.db import models
from django.forms import Textarea


class AgentTaskAdmin(admin.ModelAdmin):
    list_display = ('task_id', 'get_short_prompt', 'agent_type', 'status', 'created_at', 'updated_at', 'deal_id')
    list_filter = ('agent_type', 'status', 'created_at', 'updated_at')
    search_fields = ('prompt', 'response', 'status')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 40, 'cols': 200})},
    }

    class Media:
        css = {
            'all': ('agent/css/admin_styles.css',)
        }

    def get_short_prompt(self, obj):
        """Return the first 100 symbols of the prompt with ellipsis if longer."""
        return obj.prompt[:100] + '...' if len(obj.prompt) > 100 else obj.prompt
    get_short_prompt.short_description = 'Prompt'  # Sets column header


admin.site.register(AgentTask, AgentTaskAdmin)