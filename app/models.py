import uuid
from django.db import models

# Create your models here.


class SampleTable(models.Model):
    sample_id = models.CharField(max_length=90)
    sample_name = models.CharField(max_length=60)
    sample_email = models.EmailField(max_length=256, null=True)
    
    class Meta:
        unique_together = ('sample_id', 'sample_name',)


class ScheduledTask(models.Model):
    taskid = models.CharField(max_length=50)
    timestamp = models.DateTimeField()
