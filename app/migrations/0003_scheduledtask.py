# Generated by Django 4.2.9 on 2024-03-12 11:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_sampletable_sample_email'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScheduledTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('taskid', models.CharField(max_length=50)),
                ('timestamp', models.DateTimeField()),
            ],
        ),
    ]