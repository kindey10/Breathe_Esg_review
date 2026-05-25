from django.contrib import admin

from .models import (
    Facility,
    DataSource,
    IngestionBatch,
    RawRecord
)

admin.site.register(Facility)
admin.site.register(DataSource)
admin.site.register(IngestionBatch)
admin.site.register(RawRecord)