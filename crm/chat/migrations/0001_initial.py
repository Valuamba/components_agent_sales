# Generated by Django 5.0.3 on 2024-03-26 05:49

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('sent_at', models.DateTimeField(auto_now_add=True)),
                ('from_sender', models.CharField(choices=[('manager', 'Manager'), ('customer', 'Customer'), ('assistant', 'Assistant')], max_length=10)),
            ],
        ),
    ]