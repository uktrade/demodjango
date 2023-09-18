from django.db import models

# Create your models here.


class SampleTable(models.Model):
    sampleid = models.CharField(max_length=90)
    sample_name = models.CharField(max_length=60)
    sample_email = models.EmailField(max_length=256)
