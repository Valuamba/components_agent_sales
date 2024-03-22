from django.db import models
from django.utils import timezone


class Employee(models.Model):
    # Existing fields
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True)
    email = models.EmailField(unique=True)
    telegram_username = models.CharField(max_length=32, blank=True)
    youtrack_login = models.CharField(max_length=50)
    gitlab_username = models.CharField(max_length=50)
    telegram_id = models.CharField(max_length=32, blank=True)
    birthday_date = models.DateField()

    def __str__(self):
        return f"{self.first_name} {self.last_name} - Golang Developer"


class Team(models.Model):
    # Existing fields
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(Employee, related_name='teams')

    def __str__(self):
        return self.name