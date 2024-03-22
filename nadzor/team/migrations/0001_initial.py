# Generated by Django 5.0.3 on 2024-03-21 19:31

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('middle_name', models.CharField(blank=True, max_length=50)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('telegram_username', models.CharField(blank=True, max_length=32)),
                ('youtrack_login', models.CharField(max_length=50)),
                ('gitlab_username', models.CharField(max_length=50)),
                ('telegram_id', models.CharField(blank=True, max_length=32)),
                ('birthday_date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('members', models.ManyToManyField(related_name='teams', to='daily.dailymeetinglog')),
            ],
        ),
    ]
