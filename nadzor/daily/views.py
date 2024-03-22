from django.shortcuts import render
from django.core.serializers import serialize
from team.models import Employee

# Create your views here.


# def employee_list_view(request):
#     employees = Employee.objects.all()
#     employee_data = serialize('json', employees, fields=('first_name', 'last_name', 'email', 'telegram_username', 'youtrack_login', 'gitlab_username', 'telegram_id', 'birthday_date'))
#     return render(request, 'daily/employee_list.html', {'employee_data': employee_data})