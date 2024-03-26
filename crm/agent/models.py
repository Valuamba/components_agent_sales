from django.db import models


class AgentTask(models.Model):
    task_id = models.AutoField(primary_key=True)
    completion_cost = models.FloatField(null=True, blank=True)
    output_tokens = models.IntegerField(null=True, blank=True)
    prompt_tokens = models.IntegerField(null=True, blank=True)
    prompt = models.TextField()
    response = models.TextField(null=True, blank=True)
    agent_type = models.IntegerField()
    status = models.CharField(max_length=50)  # Adjust max_length as needed
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    deal_id = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'agent_task'