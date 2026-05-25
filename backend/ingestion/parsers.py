import csv
from datetime import datetime

from review.models import ActivityRecord, ValidationIssue, AuditEvent
from ingestion.models import RawRecord, Facility


def parse_date(value):
    if not value:
        return None

    formats = ["%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y"]

    for fmt in formats:
        try:
            return datetime.strptime(value.strip(), fmt).date()
        except ValueError:
            pass

    return None


def normalize_fuel_unit(quantity, unit):
    unit = (unit or "").strip().upper()

    if unit in ["L", "LITRE", "LITER", "LITRES", "LITERS"]:
        return quantity, "L"

    if unit == "US_GAL":
        return quantity * 3.78541, "L"

    if unit == "GAL":
        return quantity, "GAL_AMBIGUOUS"

    return None, None


def parse_sap_fuel_batch(batch):
    valid_rows = 0
    failed_rows = 0
    flagged_rows = 0

    file_path = batch.original_file.path

    with open(file_path, newline="", encoding="utf-8-sig") as csvfile:
        reader = csv.DictReader(csvfile)

        for index, row in enumerate(reader, start=2):
            raw_record = RawRecord.objects.create(
                batch=batch,
                row_number=index,
                raw_payload=row,
                parse_status="VALID",
            )

            issues = []

            plant_code = (row.get("plant_code") or "").strip()
            posting_date = parse_date(row.get("posting_date"))
            material_description = (row.get("material_description") or "").strip()
            quantity_raw = (row.get("quantity") or "").strip()
            unit = (row.get("unit") or "").strip()

            facility = Facility.objects.filter(
                organization=batch.organization,
                facility_code=plant_code,
            ).first()

            if not posting_date:
                issues.append(("ERROR", "INVALID_DATE", "Posting date is missing or invalid."))

            if not quantity_raw:
                issues.append(("ERROR", "MISSING_QUANTITY", "Fuel quantity is missing."))

            if not unit:
                issues.append(("ERROR", "MISSING_UNIT", "Fuel unit is missing."))

            try:
                quantity = float(quantity_raw)
            except ValueError:
                quantity = None
                issues.append(("ERROR", "INVALID_QUANTITY", "Fuel quantity is not numeric."))

            if quantity is not None and quantity < 0:
                issues.append(("ERROR", "NEGATIVE_QUANTITY", "Fuel quantity cannot be negative."))

            if plant_code and facility is None:
                issues.append(("WARNING", "UNKNOWN_PLANT_CODE", "Plant code is not present in the facility lookup table."))

            normalized_quantity = None
            normalized_unit = None

            if quantity is not None and unit:
                normalized_quantity, normalized_unit = normalize_fuel_unit(quantity, unit)

                if normalized_unit == "GAL_AMBIGUOUS":
                    issues.append(("WARNING", "AMBIGUOUS_GALLON_UNIT", "Unit GAL is ambiguous; US_GAL or IMP_GAL expected."))
                    normalized_quantity = None
                    normalized_unit = None

                if normalized_unit is None:
                    issues.append(("ERROR", "UNSUPPORTED_UNIT", "Fuel unit is not supported."))

            has_error = any(issue[0] == "ERROR" for issue in issues)
            has_warning = any(issue[0] == "WARNING" for issue in issues)

            if has_error:
                raw_record.parse_status = "FAILED"
                raw_record.failure_reason = "; ".join([issue[2] for issue in issues if issue[0] == "ERROR"])
                raw_record.save()

                for severity, code, message in issues:
                    ValidationIssue.objects.create(
                        raw_record=raw_record,
                        severity=severity,
                        issue_code=code,
                        message=message,
                    )

                failed_rows += 1
                continue

            review_status = "FLAGGED" if has_warning else "PENDING"

            activity = ActivityRecord.objects.create(
                organization=batch.organization,
                batch=batch,
                raw_record=raw_record,
                facility=facility,
                source_type="SAP",
                dataset_type="SAP_FUEL",
                scope="SCOPE_1",
                activity_type=material_description or "Fuel",
                activity_date_start=posting_date,
                original_quantity=quantity,
                original_unit=unit,
                normalized_quantity=round(normalized_quantity, 3),
                normalized_unit=normalized_unit,
                review_status=review_status,
                source_details={
                    "company_code": row.get("company_code"),
                    "plant_code": plant_code,
                    "document_number": row.get("document_number"),
                    "material_description": material_description,
                },
            )

            AuditEvent.objects.create(
                organization=batch.organization,
                activity_record=activity,
                actor=batch.uploaded_by if hasattr(batch, "uploaded_by") else None,
                action="CREATED",
                note="Activity record created from SAP fuel upload.",
                after_state={
                    "normalized_quantity": activity.normalized_quantity,
                    "normalized_unit": activity.normalized_unit,
                    "review_status": activity.review_status,
                },
            )

            for severity, code, message in issues:
                ValidationIssue.objects.create(
                    raw_record=raw_record,
                    activity_record=activity,
                    severity=severity,
                    issue_code=code,
                    message=message,
                )

            raw_record.parse_status = "FLAGGED" if has_warning else "VALID"
            raw_record.save()

            if has_warning:
                flagged_rows += 1
            else:
                valid_rows += 1

    batch.valid_rows = valid_rows
    batch.failed_rows = failed_rows
    batch.flagged_rows = flagged_rows
    batch.total_rows = valid_rows + failed_rows + flagged_rows
    batch.status = "COMPLETED"
    batch.save()

    return batch