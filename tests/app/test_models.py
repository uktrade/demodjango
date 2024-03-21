import threading

import pytest

from django.db import transaction
from django.db.utils import IntegrityError
from django.core.management import call_command

from app.models import SampleTable

@pytest.mark.django_db
def test_sample_table_sample_id_and_name_unique_together():
    SampleTable.objects.create(sample_id=1, sample_name="Database is connected")
    
    assert SampleTable.objects.count() == 1
    
    with transaction.atomic():
        with pytest.raises(IntegrityError):
            SampleTable.objects.create(sample_id=1, sample_name="Database is connected")
        
    assert SampleTable.objects.count() == 1
    