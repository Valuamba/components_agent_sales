# Generated by Django 5.0.3 on 2024-03-26 21:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AgentTask',
            fields=[
                ('task_id', models.AutoField(primary_key=True, serialize=False)),
                ('completion_cost', models.FloatField(blank=True, null=True)),
                ('output_tokens', models.IntegerField(blank=True, null=True)),
                ('prompt_tokens', models.IntegerField(blank=True, null=True)),
                ('prompt', models.TextField()),
                ('response', models.TextField(blank=True, null=True)),
                ('agent_type', models.IntegerField()),
                ('status', models.CharField(max_length=50)),
                ('created_at', models.DateTimeField(blank=True, null=True)),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
                ('deal_id', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'agent_task',
            },
        ),
        migrations.AddField(
            model_name='message',
            name='task_id',
            field=models.IntegerField(null=True),
        ),
    ]