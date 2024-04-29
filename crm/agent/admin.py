from django.contrib import admin
from .models import AgentTask
from django.urls import reverse

from .models import AgentTask, Issue, TaskFeedback, TaskFeedbackIssueLink, IssueGroup
from django.utils.html import format_html
from django.db import models
from django.forms import Textarea
from django import forms
from django.db.models import Prefetch


from django.contrib import admin
from django.forms import CheckboxSelectMultiple
from .models import AgentTask, TaskFeedback, Issue, TaskFeedbackIssueLink
from django.forms import Textarea
from django.utils.translation import gettext_lazy as _


class HasFeedbackFilter(admin.SimpleListFilter):
    title = _('has feedback')
    parameter_name = 'has_feedback'

    def lookups(self, request, model_admin):
        return (
            ('yes', _('Yes')),
            ('no', _('No')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.exclude(task_feedbacks__feedback='')
        if self.value() == 'no':
            return queryset.filter(task_feedbacks__feedback='')

class LikeDislikeFilter(admin.SimpleListFilter):
    title = _('like/dislike')
    parameter_name = 'like_dislike'

    def lookups(self, request, model_admin):
        return (
            ('like', _('Like')),
            ('dislike', _('Dislike')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'like':
            return queryset.filter(task_feedbacks__is_like=1)
        if self.value() == 'dislike':
            return queryset.filter(task_feedbacks__is_like=0)


class IssuesFilter(admin.SimpleListFilter):
    title = _('issues')
    parameter_name = 'issues'

    def lookups(self, request, model_admin):
        # Get a distinct list of issues used in TaskFeedbacks
        issues = Issue.objects.order_by('description').distinct()
        return [(issue.issue_id, issue.description) for issue in issues]

    def queryset(self, request, queryset):
        if self.value():
            # Filter queryset to include only those with the selected issue(s)
            return queryset.filter(task_feedbacks__issues__issue_id__in=[self.value()])


class TaskFeedbackInline(admin.StackedInline):
    model = TaskFeedback
    can_delete = False
    verbose_name_plural = 'Feedback'
    fields = ['feedback', 'is_like', 'issues']
    readonly_fields = ['feedback', 'is_like', 'issues']  # Marking all fields as read-only
    max_num = 1  # Ensures only one feedback can be linked to each AgentTask
    extra = 0


class TaskFeedbackIssueLinkInline(admin.TabularInline):
    model = TaskFeedbackIssueLink
    extra = 1  # Controls the number of extra blank forms displayed


class AgentTaskAdminForm(forms.ModelForm):
    class Meta:
        model = AgentTask
        widgets = {
            'error': forms.TextInput(attrs={'class': 'error-field'}),
            'prompt': forms.TextInput(attrs={'class': 'prompt-field'}),
            'completion_cost': forms.TextInput(attrs={'class': 'completion-field'}),
        }
        fields = '__all__'


class AgentTaskAdmin(admin.ModelAdmin):
    list_display = (
        'task_id', 'run_id', 'status_boolean', 'display_like', 'action', 'action_time_ms', 'display_feedback', 'list_issues', 'created_at'
    )
    list_filter = (
        IssuesFilter, HasFeedbackFilter, LikeDislikeFilter, 'status', 'created_at'
    )
    search_fields = ('prompt', 'response', 'status')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    inlines = (TaskFeedbackInline,)
    readonly_fields = ('deal_id',)
    # form = AgentTaskAdminForm

    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 20, 'cols': 180})},
    }

    def get_queryset(self, request):
        """Optimize queryset by prefetching related data."""
        queryset = super().get_queryset(request)
        feedback_prefetch = Prefetch('task_feedbacks', queryset=TaskFeedback.objects.prefetch_related('issues'))
        queryset = queryset.prefetch_related(feedback_prefetch)
        return queryset

    def display_like(self, obj):
        """Display if the feedback is like or not as a boolean icon."""
        feedback = next(iter(obj.task_feedbacks.all()), None)
        return feedback.is_like if feedback else None
    display_like.short_description = 'Like'
    display_like.boolean = True  # Tells Django admin to display as a boolean icon

    def display_feedback(self, obj):
        """Display the feedback text."""
        feedback = next(iter(obj.task_feedbacks.all()), None)
        return feedback.feedback if feedback and feedback.feedback else '-'

    def list_issues(self, obj):
        """Display comma-separated list of issue descriptions."""
        feedback = next(iter(obj.task_feedbacks.all()), None)
        if feedback:
            return ', '.join([issue.description for issue in feedback.issues.all()])
        return '-'

    def status_boolean(self, obj):
        return obj.status == 'Passed'

    status_boolean.short_description = 'Status'
    status_boolean.boolean = True  # Render as boolean icon


class TaskFeedbackAdmin(admin.ModelAdmin):
    list_display = ['id', 'linked_task', 'display_like', 'feedback', 'list_issues', 'created_at']
    search_fields = ['uuid', 'task__id']  # Ensure this refers to the actual foreign key to Task
    list_filter = ['created_at', 'is_like']

    def display_like(self, obj):
        """Display if the feedback is like or not as a boolean icon."""
        return obj.is_like
    display_like.short_description = 'Like'
    display_like.boolean = True  # Tells Django admin to display as a boolean icon

    def linked_task(self, obj):
        """Create a hyperlink for the task_id field to the AgentTask detail page."""
        url = reverse('admin:agent_agenttask_change', args=[obj.task.pk])
        return format_html('<a href="{}">{}</a>', url, obj.task_id)
    linked_task.short_description = 'Task ID'

    def list_issues(self, obj):
        """Retrieve all related issues and join them by comma."""
        issues = obj.issues.all()
        return ', '.join(issue.description for issue in issues)
    list_issues.short_description = 'Issues'

    def get_queryset(self, request):
        """Optimize queryset by prefetching related data."""
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('task').prefetch_related('issues')
        return queryset


class IssueAdmin(admin.ModelAdmin):
    list_display = ['issue_id', 'description', 'get_issue_group_name', 'created_at']
    search_fields = ['uuid', 'description']
    list_filter = ['created_at']

    def get_issue_group_name(self, obj):
        """Return the name of the IssueGroup associated with this Issue as a hyperlink."""
        if obj.issue_group:
            url = reverse('admin:agent_issuegroup_change', args=[obj.issue_group.pk])
            return format_html('<a href="{}">{}</a>', url, obj.issue_group.name)
        return 'No Group'
    get_issue_group_name.short_description = 'Issue Group'  # Optional: Customize column header

    def get_queryset(self, request):
        """Optimize queryset by prefetching related IssueGroup to avoid multiple DB hits."""
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('issue_group')
        return queryset


class IssueGroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'created_at']
    search_fields = ['name', 'uuid']
    list_filter = ['created_at']


admin.site.register(AgentTask, AgentTaskAdmin)
admin.site.register(TaskFeedback, TaskFeedbackAdmin)
admin.site.register(IssueGroup, IssueGroupAdmin)
admin.site.register(Issue, IssueAdmin)
