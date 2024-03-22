from django.contrib import admin
from django.forms import TextInput, Select, BaseInlineFormSet
from .models import Employee, DailyMeetingLog, Commitment, CommitmentStatus


class CommitmentInlineFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.forms:
            form.fields['description'].widget = TextInput(attrs={'placeholder': 'Default commitment'})
            form.fields['status'].widget = Select(choices=CommitmentStatus.choices)


class CommitmentInline(admin.TabularInline):
    model = Commitment
    formset = CommitmentInlineFormSet
    extra = 1  # Specifies the number of empty forms to display


@admin.register(DailyMeetingLog)
class DailyMeetingLogAdmin(admin.ModelAdmin):
    inlines = [CommitmentInline]
    # class Media:
    #     css = {
    #         'all': ('daily/css/custom_admin.css',)
    #     }
    #     js = ('daily/js/custom_admin.js',)

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        # Fetch your employees list here
        employees = Employee.objects.all()
        # Make sure to serialize or prepare your employees data as needed

        # Add the employees list to the extra_context
        extra_context = extra_context or {}
        extra_context['employees'] = employees
        return super().changeform_view(request, object_id, form_url, extra_context)