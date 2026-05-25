from rest_framework import serializers

from .models import IngestionBatch, DataSource, RawRecord
from review.models import ActivityRecord, ValidationIssue, AuditEvent


class IngestionBatchSerializer(serializers.ModelSerializer):
    data_source_name = serializers.CharField(source="data_source.name", read_only=True)

    class Meta:
        model = IngestionBatch
        fields = [
            "id",
            "data_source",
            "data_source_name",
            "dataset_type",
            "original_filename",
            "uploaded_at",
            "status",
            "total_rows",
            "valid_rows",
            "failed_rows",
            "flagged_rows",
        ]


class UploadBatchSerializer(serializers.Serializer):
    dataset_type = serializers.ChoiceField(
        choices=[
            ("SAP_FUEL", "SAP Fuel"),
            ("SAP_PROCUREMENT", "SAP Procurement"),
            ]
    )
    file = serializers.FileField()


class ValidationIssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = ValidationIssue
        fields = [
            "id",
            "severity",
            "issue_code",
            "message",
            "created_at",
        ]


class ActivityRecordSerializer(serializers.ModelSerializer):
    issues = serializers.SerializerMethodField()
    facility_name = serializers.CharField(source="facility.facility_name", read_only=True)

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
            "created_at",
        ]

    def get_issues(self, obj):
        issues = ValidationIssue.objects.filter(activity_record=obj)
        return ValidationIssueSerializer(issues, many=True).data


class RawRecordSerializer(serializers.ModelSerializer):
    issues = serializers.SerializerMethodField()

    class Meta:
        model = RawRecord
        fields = [
            "id",
            "row_number",
            "raw_payload",
            "parse_status",
            "failure_reason",
            "issues",
            "created_at",
        ]

    def get_issues(self, obj):
        issues = ValidationIssue.objects.filter(raw_record=obj)
        return ValidationIssueSerializer(issues, many=True).data