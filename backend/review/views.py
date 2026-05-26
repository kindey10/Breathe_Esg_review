from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.contrib.auth.models import User
from accounts.models import Membership
from .models import ActivityRecord, AuditEvent
from .serializers import (
    ActivityRecordDetailSerializer,
    ReviewActionSerializer,
)
def get_demo_membership(request):

    if request.user.is_authenticated:
        membership = Membership.objects.filter(user=request.user).first()

        if membership:
            return membership

    demo_user = User.objects.filter(username="kindey").first()

    if demo_user:
        return Membership.objects.filter(user=demo_user).first()

    return None

class ActivityRecordDetailView(APIView):
    def get(self, request, record_id):
        membership = get_demo_membership(request)

        if not membership:
            return Response(
                {"detail": "User is not linked to any organization."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        record = ActivityRecord.objects.filter(
            id=record_id,
            organization=membership.organization,
        ).first()

        if not record:
            return Response(
                {"detail": "Record not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ActivityRecordDetailSerializer(record)
        return Response(serializer.data)


class ApproveActivityRecordView(APIView):
    def post(self, request, record_id):
        membership = get_demo_membership(request)

        if not membership:
            return Response(
                {"detail": "User is not linked to any organization."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        record = ActivityRecord.objects.filter(
            id=record_id,
            organization=membership.organization,
        ).first()

        if not record:
            return Response(
                {"detail": "Record not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if record.is_locked:
            return Response(
                {"detail": "This record is already locked for audit."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ReviewActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        before_state = {
            "review_status": record.review_status,
            "is_locked": record.is_locked,
        }

        record.review_status = "APPROVED"
        record.is_locked = True
        actor = request.user if request.user.is_authenticated else User.objects.filter(username="kindey").first()
        record.approved_by = actor
        record.save()

        after_state = {
            "review_status": record.review_status,
            "is_locked": record.is_locked,
            "approved_by": actor.username if actor else "demo",
        }

        AuditEvent.objects.create(
            organization=membership.organization,
            activity_record=record,
            actor=actor,
            action="APPROVED",
            note=serializer.validated_data.get("note", "Approved and locked for audit."),
            before_state=before_state,
            after_state=after_state,
        )

        AuditEvent.objects.create(
            organization=membership.organization,
            activity_record=record,
            actor=request.user,
            action="LOCKED",
            note="Record locked after analyst approval.",
            before_state=before_state,
            after_state=after_state,
        )

        return Response(ActivityRecordDetailSerializer(record).data)


class RejectActivityRecordView(APIView):
    def post(self, request, record_id):
        membership = get_demo_membership(request)

        if not membership:
            return Response(
                {"detail": "User is not linked to any organization."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        record = ActivityRecord.objects.filter(
            id=record_id,
            organization=membership.organization,
        ).first()

        if not record:
            return Response(
                {"detail": "Record not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if record.is_locked:
            return Response(
                {"detail": "Locked records cannot be rejected."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ReviewActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        before_state = {
            "review_status": record.review_status,
            "is_locked": record.is_locked,
        }

        record.review_status = "REJECTED"
        record.save()

        after_state = {
            "review_status": record.review_status,
            "is_locked": record.is_locked,
        }

        AuditEvent.objects.create(
            organization=membership.organization,
            activity_record=record,
            actor=request.user,
            action="REJECTED",
            note=serializer.validated_data.get("note", "Rejected by analyst."),
            before_state=before_state,
            after_state=after_state,
        )

        return Response(ActivityRecordDetailSerializer(record).data)