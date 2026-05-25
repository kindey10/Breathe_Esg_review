from django.db import models
from accounts.models import Organization


class Facility(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    facility_code = models.CharField(max_length=100)
    facility_name = models.CharField(max_length=255)
    city = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.facility_code} - {self.facility_name}"


class DataSource(models.Model):
    SOURCE_CHOICES = [
        ('SAP', 'SAP'),
        ('UTILITY', 'Utility'),
        ('TRAVEL', 'Travel'),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    source_type = models.CharField(max_length=50, choices=SOURCE_CHOICES)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class IngestionBatch(models.Model):
    STATUS_CHOICES = [
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE)

    dataset_type = models.CharField(max_length=100)

    original_file = models.FileField(upload_to='uploads/')
    original_filename = models.CharField(max_length=255)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PROCESSING'
    )

    total_rows = models.IntegerField(default=0)
    valid_rows = models.IntegerField(default=0)
    failed_rows = models.IntegerField(default=0)
    flagged_rows = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.dataset_type} - {self.original_filename}"


class RawRecord(models.Model):
    PARSE_STATUS_CHOICES = [
        ('VALID', 'Valid'),
        ('FLAGGED', 'Flagged'),
        ('FAILED', 'Failed'),
    ]

    batch = models.ForeignKey(IngestionBatch, on_delete=models.CASCADE)

    row_number = models.IntegerField()

    raw_payload = models.JSONField()

    parse_status = models.CharField(
        max_length=20,
        choices=PARSE_STATUS_CHOICES
    )

    failure_reason = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Row {self.row_number}"