# Generated by Django 5.0.3 on 2024-03-26 20:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Deal',
            fields=[
                ('deal_id', models.CharField(max_length=50, primary_key=True, serialize=False, unique=True)),
                ('subject', models.CharField(max_length=255)),
                ('customer', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('sent_at', models.DateTimeField(auto_now_add=True)),
                ('from_sender', models.CharField(choices=[('manager', 'Manager'), ('customer', 'Customer'), ('assistant', 'Assistant')], max_length=10)),
                ('deal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='chat.deal')),
            ],
        ),
    ]
