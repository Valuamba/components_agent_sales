from django.contrib import admin
from team.models import Employee, Team


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'youtrack_login', 'gitlab_username', 'birthday_date')
    search_fields = ('first_name', 'last_name', 'email')
    # list_filter = ('teams',)


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name',)
    filter_horizontal = ('members',)