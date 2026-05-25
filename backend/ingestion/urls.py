from django.urls import path

from .views import (
    UploadBatchView,
    BatchListView,
    ActivityRecordListView,
    FailedRawRecordListView,
)

urlpatterns = [
    path("upload/", UploadBatchView.as_view(), name="upload-batch"),
    path("batches/", BatchListView.as_view(), name="batch-list"),
    path("records/", ActivityRecordListView.as_view(), name="activity-record-list"),
    path("failed-rows/", FailedRawRecordListView.as_view(), name="failed-raw-record-list"),
]