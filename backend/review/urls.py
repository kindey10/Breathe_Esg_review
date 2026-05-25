from django.urls import path

from .views import (
    ActivityRecordDetailView,
    ApproveActivityRecordView,
    RejectActivityRecordView,
)

urlpatterns = [
    path("records/<int:record_id>/", ActivityRecordDetailView.as_view(), name="record-detail"),
    path("records/<int:record_id>/approve/", ApproveActivityRecordView.as_view(), name="record-approve"),
    path("records/<int:record_id>/reject/", RejectActivityRecordView.as_view(), name="record-reject"),
]