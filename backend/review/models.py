from django.db import models
from django.contrib.auth.models import User

from accounts.models import Organization
from ingestion.models import (
    IngestionBatch,
    RawRecord,
    Facility
)


class ActivityRecord(models.Model):
    REVIEW_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('FLAGGED', 'Flagged'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    batch = models.ForeignKey(IngestionBatch, on_delete=models.CASCADE)

    raw_record = models.ForeignKey(RawRecord, on_delete=models.CASCADE)

    facility = models.ForeignKey(
        Facility,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    source_type = models.CharField(max_length=50)

    dataset_type = models.CharField(max_length=100)

    scope = models.CharField(max_length=50)

    activity_type = models.CharField(max_length=100)

    activity_date_start = models.DateField()
    activity_date_end = models.DateField(null=True, blank=True)

    original_quantity = models.FloatField(
        null=True,
        blank=True
    )

    original_unit = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    normalized_quantity = models.FloatField(
        null=True,
        blank=True
    )

    normalized_unit = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )
    source_details = models.JSONField(default=dict, blank=True)

    review_status = models.CharField(
        max_length=20,
        choices=REVIEW_STATUS_CHOICES,
        default='PENDING'
    )

    is_locked = models.BooleanField(default=False)

    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.activity_type} - {self.scope}"


class ValidationIssue(models.Model):
    SEVERITY_CHOICES = [
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
    ]

    raw_record = models.ForeignKey(
        RawRecord,
        on_delete=models.CASCADE
    )

    activity_record = models.ForeignKey(
        ActivityRecord,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES
    )

    issue_code = models.CharField(max_length=100)

    message = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.issue_code


class AuditEvent(models.Model):
    ACTION_CHOICES = [
        ('CREATED', 'Created'),
        ('EDITED', 'Edited'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('LOCKED', 'Locked'),
    ]

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE
    )

    activity_record = models.ForeignKey(
        ActivityRecord,
        on_delete=models.CASCADE
    )

    actor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )

    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES
    )

    note = models.TextField(blank=True, null=True)
    before_state = models.JSONField(null=True, blank=True)
    after_state = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.action