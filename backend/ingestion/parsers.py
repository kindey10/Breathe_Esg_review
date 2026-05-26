import json
import csv
from datetime import datetime

from review.models import ActivityRecord, ValidationIssue, AuditEvent
from ingestion.models import RawRecord, Facility
import csv

from django.utils.dateparse import parse_date

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
def parse_travel_batch(batch):
    valid_rows = 0
    failed_rows = 0
    flagged_rows = 0

    airport_distances = {
        ("DEL", "BOM"): 1138,
        ("BOM", "DEL"): 1138,
        ("DEL", "BLR"): 1700,
        ("BLR", "DEL"): 1700,
    }

    file_path = batch.original_file.path

    with open(file_path, encoding="utf-8") as jsonfile:
        data = json.load(jsonfile)

    trips = data.get("trips", [])

    for index, trip in enumerate(trips, start=1):
        raw_record = RawRecord.objects.create(
            batch=batch,
            row_number=index,
            raw_payload=trip,
            parse_status="VALID",
        )

        issues = []
        travel_type = (trip.get("type") or "").strip().upper()

        activity_type = "Business travel"
        normalized_quantity = None
        normalized_unit = None
        start_date = None
        end_date = None

        if travel_type == "AIR":
            origin = (trip.get("start_city_code") or "").strip().upper()
            destination = (trip.get("end_city_code") or "").strip().upper()
            start_date = parse_date((trip.get("start_date") or "")[:10])

            if not origin or not destination:
                issues.append(("ERROR", "MISSING_AIRPORT_CODE", "Origin or destination airport code is missing."))

            distance = airport_distances.get((origin, destination))

            if distance is None:
                issues.append(("WARNING", "UNKNOWN_AIRPORT_ROUTE", "Airport route is not in the prototype distance lookup."))

            if not start_date:
                issues.append(("ERROR", "INVALID_TRAVEL_DATE", "Flight date is missing or invalid."))

            activity_type = f"Flight {origin} to {destination}"
            normalized_quantity = distance
            normalized_unit = "km"

        elif travel_type == "HOTEL":
            city = trip.get("city")
            start_date = parse_date(trip.get("start_date"))
            end_date = parse_date(trip.get("end_date"))
            rooms = trip.get("num_rooms")

            if not start_date or not end_date:
                issues.append(("ERROR", "INVALID_HOTEL_DATES", "Hotel dates are missing or invalid."))

            if start_date and end_date and end_date <= start_date:
                issues.append(("ERROR", "INVALID_HOTEL_DATE_ORDER", "Hotel checkout must be after check-in."))

            try:
                rooms = int(rooms)
            except (TypeError, ValueError):
                rooms = None
                issues.append(("WARNING", "MISSING_ROOM_COUNT", "Room count is missing or invalid."))

            if start_date and end_date and rooms:
                nights = (end_date - start_date).days
                normalized_quantity = nights * rooms
                normalized_unit = "room_nights"

            activity_type = f"Hotel stay - {city or 'Unknown city'}"

        elif travel_type == "GROUND":
            mode = trip.get("transport_mode") or "GROUND"
            distance_raw = trip.get("distance_value")
            distance_unit = (trip.get("distance_unit") or "").strip().lower()

            try:
                distance = float(distance_raw)
            except (TypeError, ValueError):
                distance = None
                issues.append(("WARNING", "MISSING_GROUND_DISTANCE", "Ground transport distance is missing or invalid."))

            if distance is not None:
                if distance_unit == "km":
                    normalized_quantity = distance
                    normalized_unit = "km"
                elif distance_unit in ["mile", "miles", "mi"]:
                    normalized_quantity = distance * 1.60934
                    normalized_unit = "km"
                else:
                    issues.append(("ERROR", "UNSUPPORTED_DISTANCE_UNIT", "Ground transport distance unit is unsupported."))

            start_date = parse_date(trip.get("start_date")) or parse_date("2026-02-12")
            activity_type = f"Ground transport - {mode}"

        else:
            issues.append(("ERROR", "UNSUPPORTED_TRAVEL_TYPE", "Travel type is not supported."))

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
            facility=None,
            source_type="TRAVEL",
            dataset_type="TRAVEL",
            scope="SCOPE_3",
            activity_type=activity_type,
            activity_date_start=start_date,
            activity_date_end=end_date,
            original_quantity=normalized_quantity,
            original_unit=normalized_unit,
            normalized_quantity=round(normalized_quantity, 3) if normalized_quantity is not None else None,
            normalized_unit=normalized_unit,
            review_status=review_status,
            source_details={
                "trip_id": trip.get("trip_id"),
                "travel_type": travel_type,
                "scope_category": "Category 6 - Business Travel",
                "raw_trip": trip,
            },
        )

        AuditEvent.objects.create(
            organization=batch.organization,
            activity_record=activity,
            actor=batch.uploaded_by,
            action="CREATED",
            note="Activity record created from corporate travel upload.",
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

def parse_sap_activity_batch(batch):
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

            source_category = (row.get("source_category") or "").strip().upper()
            activity_type = (row.get("activity_type") or "").strip()
            quantity_raw = (row.get("quantity") or "").strip()
            unit = (row.get("unit") or "").strip()
            facility_name = (row.get("facility_name") or "").strip()
            activity_date = parse_date(row.get("activity_date"))
            vendor_name = (row.get("vendor_name") or "").strip()
            material_group = (row.get("material_group") or "").strip()

            if not activity_date:
                issues.append(("ERROR", "MISSING_OR_INVALID_DATE", "Activity date is missing or invalid."))

            if not facility_name:
                issues.append(("ERROR", "MISSING_FACILITY", "Facility name is missing."))

            if not quantity_raw:
                issues.append(("ERROR", "MISSING_QUANTITY", "Quantity or amount is missing."))

            try:
                quantity = float(quantity_raw)
            except ValueError:
                quantity = None
                issues.append(("ERROR", "INVALID_QUANTITY", "Quantity is not numeric."))

            if quantity is not None and quantity < 0:
                issues.append(("ERROR", "NEGATIVE_VALUE", "Negative values cannot be approved without correction."))

            if source_category == "FUEL":
                scope = "SCOPE_1"

                normalized_quantity = None
                normalized_unit = None

                if quantity is not None:
                    normalized_quantity, normalized_unit = normalize_fuel_unit(quantity, unit)

                    if normalized_unit == "GAL_AMBIGUOUS":
                        issues.append(("WARNING", "AMBIGUOUS_GALLON_UNIT", "Gallon unit is ambiguous; expected US_GAL."))
                        normalized_quantity = None
                        normalized_unit = None

                    if normalized_unit is None:
                        issues.append(("ERROR", "UNSUPPORTED_FUEL_UNIT", "Fuel unit is not supported."))

                    if quantity > 100000:
                        issues.append(("WARNING", "FUEL_OUTLIER", "Fuel quantity is unusually high and needs review."))

            elif source_category == "PROCUREMENT":
                scope = "SCOPE_3"
                normalized_quantity = quantity
                normalized_unit = unit

                if unit.upper() != "INR":
                    issues.append(("ERROR", "UNSUPPORTED_CURRENCY", "Only INR procurement values are supported in this prototype."))

                if not vendor_name:
                    issues.append(("WARNING", "MISSING_VENDOR", "Vendor name is missing."))

                if not material_group:
                    issues.append(("WARNING", "MISSING_MATERIAL_GROUP", "Material group is missing."))

                if quantity == 0:
                    issues.append(("WARNING", "ZERO_PROCUREMENT_AMOUNT", "Procurement amount is zero."))

                if quantity is not None and quantity > 10000000:
                    issues.append(("WARNING", "PROCUREMENT_OUTLIER", "Procurement amount is unusually high."))

            else:
                scope = "UNKNOWN"
                normalized_quantity = None
                normalized_unit = None
                issues.append(("ERROR", "UNKNOWN_SAP_CATEGORY", "SAP row must be FUEL or PROCUREMENT."))

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
                facility=None,
                source_type="SAP",
                dataset_type="SAP_ACTIVITY",
                scope=scope,
                activity_type=activity_type or source_category,
                activity_date_start=activity_date,
                original_quantity=quantity,
                original_unit=unit,
                normalized_quantity=round(normalized_quantity, 3) if normalized_quantity is not None else None,
                normalized_unit=normalized_unit,
                review_status=review_status,
                source_details={
                    "source_category": source_category,
                    "facility_name": facility_name,
                    "vendor_name": vendor_name,
                    "material_group": material_group,
                    "standardized_as": "Fuel in litres" if source_category == "FUEL" else "Procurement spend in INR",
                },
            )

            AuditEvent.objects.create(
                organization=batch.organization,
                activity_record=activity,
                actor=batch.uploaded_by,
                action="CREATED",
                note="Standardized SAP activity record created.",
                after_state={
                    "raw_value": f"{quantity} {unit}",
                    "standard_value": f"{activity.normalized_quantity} {activity.normalized_unit}",
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


def parse_travel_activity_batch(batch):
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

            employee_id = (row.get("employee_id") or "").strip()
            travel_type = (row.get("travel_type") or "").strip()
            distance_raw = (row.get("distance_km") or "").strip()
            facility_name = (row.get("facility_name") or "").strip()
            travel_date = parse_date(row.get("travel_date"))
            travel_class = (row.get("class") or "").strip()

            if not travel_date:
                issues.append(("ERROR", "MISSING_TRAVEL_DATE", "Travel date is missing or invalid."))

            if not facility_name:
                issues.append(("WARNING", "MISSING_FACILITY", "Facility name is missing."))

            try:
                distance = float(distance_raw)
            except ValueError:
                distance = None
                issues.append(("ERROR", "INVALID_DISTANCE", "Distance is not numeric."))

            if distance is not None and distance < 0:
                issues.append(("ERROR", "NEGATIVE_DISTANCE", "Travel distance cannot be negative."))

            if distance is not None and distance > 10000:
                issues.append(("WARNING", "TRAVEL_DISTANCE_OUTLIER", "Travel distance is unusually high."))

            if travel_class.upper() in ["UNKNOWN", ""]:
                issues.append(("WARNING", "UNKNOWN_TRAVEL_CLASS", "Travel class is missing or unknown."))

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
                facility=None,
                source_type="TRAVEL",
                dataset_type="TRAVEL_ACTIVITY",
                scope="SCOPE_3",
                activity_type=f"{travel_type} travel",
                activity_date_start=travel_date,
                original_quantity=distance,
                original_unit="km",
                normalized_quantity=distance,
                normalized_unit="km",
                review_status=review_status,
                source_details={
                    "employee_id": employee_id,
                    "facility_name": facility_name,
                    "travel_class": travel_class,
                    "standardized_as": "Business travel distance in km",
                },
            )

            AuditEvent.objects.create(
                organization=batch.organization,
                activity_record=activity,
                actor=batch.uploaded_by,
                action="CREATED",
                note="Standardized travel activity record created.",
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