from django.db import models
import uuid


STATUS_CHOICES = (
    ('Failed', 'Failed'),
    ('Passed', 'Passed'),
)


class Email(models.Model):
    imap_server = models.CharField(max_length=255)
    imap_user = models.CharField(max_length=255)
    subject = models.TextField(null=True, blank=True)
    body = models.TextField(null=True, blank=True)
    from_address = models.CharField(max_length=255, null=True, blank=True)
    to_address = models.CharField(max_length=255, null=True, blank=True)
    date = models.DateTimeField(null=True, blank=True)
    message_id = models.CharField(max_length=255, unique=True)
    spam_flag = models.BooleanField(null=True, blank=True)
    spam_score = models.FloatField(null=True, blank=True)
    gpt_spam_flag = models.BooleanField(null=True, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    folder = models.CharField(max_length=255, null=True, blank=True)
    body_hash = models.CharField(max_length=255, null=True, blank=True)
    is_error = models.BooleanField(default=False)
    error_msg = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'emails'
        constraints = [
            models.UniqueConstraint(fields=['message_id'], name='emails_message_id_key')
        ]
        verbose_name = "Email"
        verbose_name_plural = "Emails"

    def __str__(self):
        return f"{self.subject} - {self.from_address}"


class LLMRun(models.Model):
    run_id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    status = models.IntegerField()
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    deal_id = models.CharField(max_length=200, blank=True, null=True)
    # deal = models.ForeignKey("Deal", on_delete=models.CASCADE, related_name="runs")

    # agent_tasks = models.ManyToManyField("AgentTask", related_name="runs")
    # run_feedbacks = models.ManyToManyField("TaskFeedback", related_name="runs")

    class Meta:
        db_table = 'runs'

    def __str__(self):
        return f"LLMRun {self.uuid}"


class AgentTask(models.Model):
    run_id = models.IntegerField(null=True)
    task_id = models.AutoField(primary_key=True)
    completion_cost = models.FloatField(null=True, blank=True)
    output_tokens = models.IntegerField(null=True, blank=True)
    prompt_tokens = models.IntegerField(null=True, blank=True)
    error = models.TextField(null=True, blank=True)
    action_time_ms = models.IntegerField(null=True, blank=True)
    action = models.CharField(null=True, blank=True, max_length=200)
    prompt = models.TextField()
    response = models.TextField(null=True, blank=True)
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='Failed'
    )
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    deal_id = models.CharField(null=True, blank=True, max_length=200)

    class Meta:
        db_table = 'agent_task'


class IssueGroup(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        db_table = 'issue_group'


class TaskFeedback(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    task = models.ForeignKey('AgentTask', related_name='task_feedbacks', on_delete=models.CASCADE)
    run = models.ForeignKey('LLMRun', related_name='run_feedbacks', on_delete=models.CASCADE)
    feedback = models.TextField(null=True, blank=True)
    is_like = models.IntegerField(choices=((0, 'Dislike'), (1, 'Like')))
    # is_like = models.BooleanField(default=False)
    issues = models.ManyToManyField('Issue', through='TaskFeedbackIssueLink')

    class Meta:
        db_table = 'task_feedback'


class IssueGroup(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'issue_group'


class Issue(models.Model):
    issue_id = models.AutoField(primary_key=True)  # Explicitly defining issue_id as the primary key
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    description = models.CharField(max_length=1024)
    issue_group = models.ForeignKey('IssueGroup', related_name='issues', on_delete=models.CASCADE)

    class Meta:
        db_table = 'issue'

    def __str__(self):
        return f"{self.description}"


class TaskFeedbackIssueLink(models.Model):
    task_feedback = models.ForeignKey(TaskFeedback, on_delete=models.CASCADE, primary_key=True)
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)

    class Meta:
        db_table = 'taskfeedback_issue_link'
        unique_together = ('task_feedback', 'issue')