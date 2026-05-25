from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from accounts.models import Membership
from .models import DataSource, IngestionBatch, RawRecord
from review.models import ActivityRecord, ValidationIssue
from .serializers import (
    IngestionBatchSerializer,
    UploadBatchSerializer,
    ActivityRecordSerializer,
    RawRecordSerializer,
)
from .parsers import (
    parse_sap_fuel_batch,
    parse_sap_procurement_batch,
    parse_utility_electricity_batch,
    parse_travel_batch,
)


class UploadBatchView(APIView):
    def post(self, request):
        serializer = UploadBatchSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        membership = Membership.objects.filter(user=request.user).first()

        if not membership:
            return Response(
                {"detail": "User is not linked to any organization."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        dataset_type = serializer.validated_data["dataset_type"]
        uploaded_file = serializer.validated_data["file"]

        if dataset_type in ["SAP_FUEL", "SAP_PROCUREMENT"]:
            source_type = "SAP"
        elif dataset_type == "UTILITY_ELECTRICITY":
            source_type = "UTILITY"    
        elif dataset_type == "TRAVEL":
            source_type = "TRAVEL"
        else:
            return Response(
                {"detail": "Unsupported dataset type."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data_source = DataSource.objects.filter(
            organization=membership.organization,
            source_type=source_type,
        ).first()

        if not data_source:
            return Response(
                {"detail": "Data source not configured for this organization."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        batch = IngestionBatch.objects.create(
            organization=membership.organization,
            data_source=data_source,
            dataset_type=dataset_type,
            original_file=uploaded_file,
            original_filename=uploaded_file.name,
            uploaded_by=request.user,
            status="PROCESSING",
        )

        if dataset_type == "SAP_FUEL":
            parse_sap_fuel_batch(batch)
        if dataset_type == "SAP_PROCUREMENT":
            parse_sap_procurement_batch(batch)
        if dataset_type == "UTILITY_ELECTRICITY":
            parse_utility_electricity_batch(batch)
        if dataset_type == "TRAVEL":
            parse_travel_batch(batch)

        response_data = IngestionBatchSerializer(batch).data
        return Response(response_data, status=status.HTTP_201_CREATED)


class BatchListView(APIView):
    def get(self, request):
        membership = Membership.objects.filter(user=request.user).first()

        if not membership:
            return Response([], status=status.HTTP_200_OK)

        batches = IngestionBatch.objects.filter(
            organization=membership.organization
        ).order_by("-uploaded_at")

        serializer = IngestionBatchSerializer(batches, many=True)
        return Response(serializer.data)


class ActivityRecordListView(APIView):
    def get(self, request):
        membership = Membership.objects.filter(user=request.user).first()

        if not membership:
            return Response([], status=status.HTTP_200_OK)

        records = ActivityRecord.objects.filter(
            organization=membership.organization
        ).order_by("-created_at")

        review_status = request.query_params.get("review_status")
        dataset_type = request.query_params.get("dataset_type")

        if review_status:
            records = records.filter(review_status=review_status)

        if dataset_type:
            records = records.filter(dataset_type=dataset_type)

        serializer = ActivityRecordSerializer(records, many=True)
        return Response(serializer.data)


class FailedRawRecordListView(APIView):
    def get(self, request):
        membership = Membership.objects.filter(user=request.user).first()

        if not membership:
            return Response([], status=status.HTTP_200_OK)

        failed_rows = RawRecord.objects.filter(
            batch__organization=membership.organization,
            parse_status="FAILED",
        ).order_by("-created_at")

        serializer = RawRecordSerializer(failed_rows, many=True)
        return Response(serializer.data)
class DashboardSummaryView(APIView):
    def get(self, request):
        membership = Membership.objects.filter(user=request.user).first()

        if not membership:
            return Response(
                {"detail": "User is not linked to any organization."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        organization = membership.organization

        total_batches = IngestionBatch.objects.filter(
            organization=organization
        ).count()

        pending_records = ActivityRecord.objects.filter(
            organization=organization,
            review_status="PENDING",
        ).count()

        flagged_records = ActivityRecord.objects.filter(
            organization=organization,
            review_status="FLAGGED",
        ).count()

        approved_records = ActivityRecord.objects.filter(
            organization=organization,
            review_status="APPROVED",
            is_locked=True,
        ).count()

        rejected_records = ActivityRecord.objects.filter(
            organization=organization,
            review_status="REJECTED",
        ).count()

        failed_rows = RawRecord.objects.filter(
            batch__organization=organization,
            parse_status="FAILED",
        ).count()

        total_issues = ValidationIssue.objects.filter(
            raw_record__batch__organization=organization
        ).count()

        return Response({
            "organization": organization.name,
            "total_batches": total_batches,
            "pending_records": pending_records,
            "flagged_records": flagged_records,
            "approved_locked_records": approved_records,
            "rejected_records": rejected_records,
            "failed_rows": failed_rows,
            "total_issues": total_issues,
        })