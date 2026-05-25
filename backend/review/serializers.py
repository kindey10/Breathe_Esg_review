from rest_framework import serializers

from .models import ActivityRecord, AuditEvent, ValidationIssue


class AuditEventSerializer(serializers.ModelSerializer):
    actor_name = serializers.CharField(source="actor.username", read_only=True)

    class Meta:
        model = AuditEvent
        fields = [
            "id",
            "actor_name",
            "action",
            "note",
            "before_state",
            "after_state",
            "created_at",
        ]


class ReviewActionSerializer(serializers.Serializer):
    note = serializers.CharField(required=False, allow_blank=True)


class ActivityRecordDetailSerializer(serializers.ModelSerializer):
    facility_name = serializers.CharField(source="facility.facility_name", read_only=True)
    audit_events = serializers.SerializerMethodField()
    issues = serializers.SerializerMethodField()

    class Meta:
        model = ActivityRecord
        fields = [
            "id",
            "source_type",
            "dataset_type",
            "scope",
            "activity_type",
            "activity_date_start",
            "activity_date_end",
            "original_quantity",
            "original_unit",
            "normalized_quantity",
            "normalized_unit",
            "review_status",
            "is_locked",
            "facility_name",
            "source_details",
            "issues",
            "audit_events",
            "created_at",
        ]

    def get_audit_events(self, obj):
        events = AuditEvent.objects.filter(activity_record=obj).order_by("-created_at")
        return AuditEventSerializer(events, many=True).data

    def get_issues(self, obj):
        issues = ValidationIssue.objects.filter(activity_record=obj)
        return [
            {
                "severity": issue.severity,
                "issue_code": issue.issue_code,
                "message": issue.message,
            }
            for issue in issues
        ]