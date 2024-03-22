from django.contrib import admin
from team.models import Employee, Team


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'youtrack_login', 'gitlab_username', 'birthday_date')
    search_fields = ('first_name', 'last_name', 'email')
    # list_filter = ('teams',)

    # def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
    #     # Fetch your employees list here
    #     employees = Employee.objects.all()
    #     # Make sure to serialize or prepare your employees data as needed
    #
    #     # Add the employees list to the extra_context
    #     extra_context = extra_context or {}
    #     extra_context['employees'] = employees
    #     return super().changeform_view(request, object_id, form_url, extra_context)
    #
    # def save_model(self, request, obj, form, change):
    #     super().save_model(request, obj, form, change)
    #     for key, value in request.POST.items():
    #         if key.startswith('customField-'):
    #             pass


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name',)
    filter_horizontal = ('members',)