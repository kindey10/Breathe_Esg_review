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

def parse_sap_procurement_batch(batch):
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
            material_group = (row.get("material_group") or "").strip()
            description = (row.get("description") or "").strip()
            amount_raw = (row.get("net_amount") or "").strip()
            currency = (row.get("currency") or "").strip()

            facility = Facility.objects.filter(
                organization=batch.organization,
                facility_code=plant_code,
            ).first()

            if not posting_date:
                issues.append(("ERROR", "INVALID_DATE", "Posting date is missing or invalid."))

            if not amount_raw:
                issues.append(("ERROR", "MISSING_AMOUNT", "Procurement amount is missing."))

            if not currency:
                issues.append(("ERROR", "MISSING_CURRENCY", "Currency is missing."))

            try:
                amount = float(amount_raw)
            except ValueError:
                amount = None
                issues.append(("ERROR", "INVALID_AMOUNT", "Procurement amount is not numeric."))

            if amount is not None and amount < 0:
                issues.append(("ERROR", "NEGATIVE_AMOUNT", "Procurement amount cannot be negative."))

            if plant_code and facility is None:
                issues.append(("WARNING", "UNKNOWN_PLANT_CODE", "Plant code is not present in the facility lookup table."))

            if not material_group:
                issues.append(("WARNING", "MISSING_MATERIAL_GROUP", "Material group is missing, so procurement classification is uncertain."))

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
                dataset_type="SAP_PROCUREMENT",
                scope="SCOPE_3",
                activity_type=description or "Purchased goods and services",
                activity_date_start=posting_date,
                original_quantity=amount,
                original_unit=currency,
                normalized_quantity=amount,
                normalized_unit=currency,
                review_status=review_status,
                source_details={
                    "company_code": row.get("company_code"),
                    "plant_code": plant_code,
                    "purchase_order": row.get("purchase_order"),
                    "vendor_code": row.get("vendor_code"),
                    "material_group": material_group,
                    "scope_category": "Category 1 - Purchased Goods and Services",
                },
            )

            AuditEvent.objects.create(
                organization=batch.organization,
                activity_record=activity,
                actor=batch.uploaded_by,
                action="CREATED",
                note="Activity record created from SAP procurement upload.",
                after_state={
                    "amount": activity.normalized_quantity,
                    "currency": activity.normalized_unit,
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

def normalize_electricity_unit(quantity, unit):
    unit = (unit or "").strip().upper()

    if unit == "KWH":
        return quantity, "kWh"

    if unit == "MWH":
        return quantity * 1000, "kWh"

    return None, None


def parse_utility_electricity_batch(batch):
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

            facility_code = (row.get("facility_code") or "").strip()
            meter_id = (row.get("meter_id") or "").strip()
            start_date = parse_date(row.get("billing_period_start"))
            end_date = parse_date(row.get("billing_period_end"))
            usage_raw = (row.get("usage_value") or "").strip()
            unit = (row.get("usage_unit") or "").strip()

            facility = Facility.objects.filter(
                organization=batch.organization,
                facility_code=facility_code,
            ).first()

            if facility_code and facility is None:
                issues.append(("WARNING", "UNKNOWN_FACILITY_CODE", "Facility code is not present in the lookup table."))

            if not meter_id:
                issues.append(("ERROR", "MISSING_METER_ID", "Meter ID is missing."))

            if not start_date or not end_date:
                issues.append(("ERROR", "INVALID_BILLING_PERIOD", "Billing period dates are missing or invalid."))

            if start_date and end_date and end_date < start_date:
                issues.append(("ERROR", "INVALID_BILLING_PERIOD_ORDER", "Billing period end date is before start date."))

            if not usage_raw:
                issues.append(("ERROR", "MISSING_USAGE", "Electricity usage value is missing."))

            try:
                usage = float(usage_raw)
            except ValueError:
                usage = None
                issues.append(("ERROR", "INVALID_USAGE", "Electricity usage is not numeric."))

            if usage is not None and usage < 0:
                issues.append(("WARNING", "NEGATIVE_ELECTRICITY_USAGE", "Electricity usage is negative and requires analyst review."))

            normalized_quantity = None
            normalized_unit = None

            if usage is not None and unit:
                normalized_quantity, normalized_unit = normalize_electricity_unit(usage, unit)

                if normalized_unit is None:
                    issues.append(("ERROR", "UNSUPPORTED_ELECTRICITY_UNIT", "Electricity unit is not supported."))

            if not unit:
                issues.append(("ERROR", "MISSING_UNIT", "Electricity unit is missing."))

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
                source_type="UTILITY",
                dataset_type="UTILITY_ELECTRICITY",
                scope="SCOPE_2",
                activity_type="Purchased electricity",
                activity_date_start=start_date,
                activity_date_end=end_date,
                original_quantity=usage,
                original_unit=unit,
                normalized_quantity=round(normalized_quantity, 3),
                normalized_unit=normalized_unit,
                review_status=review_status,
                source_details={
                    "account_id": row.get("account_id"),
                    "meter_id": meter_id,
                    "facility_code": facility_code,
                    "tariff": row.get("tariff"),
                    "billed_amount": row.get("billed_amount"),
                    "currency": row.get("currency"),
                },
            )

            AuditEvent.objects.create(
                organization=batch.organization,
                activity_record=activity,
                actor=batch.uploaded_by,
                action="CREATED",
                note="Activity record created from utility electricity upload.",
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