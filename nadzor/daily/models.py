from django.db import models
from django.utils import timezone

from team.models import Team, Employee


class DailyMeetingLog(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='daily_meetings')
    date = models.DateField(default=timezone.now)
    notes = models.TextField(blank=True, help_text="General notes about the meeting.")

    def __str__(self):
        return f"{self.team.name} Meeting - {self.date.strftime('%Y-%m-%d')}"


class CommitmentStatus(models.TextChoices):
    COMPLETE = 'Complete', 'Complete'
    CANCELED = 'Canceled', 'Canceled'
    BLOCKED = 'Blocked', 'Blocked'
    PENDING = 'Pending', 'Pending'  # For commitments that are planned but not yet completed, canceled, or blocked


class Commitment(models.Model):
    meeting_log = models.ForeignKey(DailyMeetingLog, on_delete=models.CASCADE, related_name='commitments')
    description = models.TextField(help_text="Description of the commitment made by the dailymeetinglog.")
    status = models.CharField(max_length=10, choices=CommitmentStatus.choices, default=CommitmentStatus.PENDING)
    responsible_person = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='commitments')

    def __str__(self):
        return f"Commitment: {self.description[:30]} - Status: {self.status}"