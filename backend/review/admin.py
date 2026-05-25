from django.contrib import admin

from .models import (
    ActivityRecord,
    ValidationIssue,
    AuditEvent
)

admin.site.register(ActivityRecord)
admin.site.register(ValidationIssue)
admin.site.register(AuditEvent)