# Decisions

## Why CSV for SAP?

SAP exports are commonly shared as spreadsheet or flat-file exports during onboarding. CSV uploads are realistic, easy to validate and easier for analysts to debug than pretending to build a live SAP integration without credentials.

## Why separate SAP fuel and procurement files?

Both datasets originate from SAP, but fuel and procurement have different meanings, validation rules and Scope classifications. Fuel data uses quantity and unit normalization, while procurement uses amount, currency and material categorization.

## Why CSV for utility electricity?

Facilities teams commonly export utility data from portals into structured CSV files. CSV avoids OCR complexity and allows more reliable validation of billing periods, units and meter identifiers.

## Why JSON for travel?

Corporate travel platforms such as SAP Concur expose structured itinerary data through APIs. Since this prototype does not have enterprise API credentials, a realistic JSON snapshot simulates the API response format honestly.

## Why no emissions calculation?

The assignment specifically emphasizes ingestion, normalization and review workflows. Accurate carbon calculations require emissions-factor governance, methodology choices and factor versioning, which are outside the scope of this prototype.

## Why store raw rows separately from normalized rows?

Auditors and analysts must be able to trace every cleaned activity record back to the exact original uploaded row.

## Why lock approved rows?

Approved records represent audit-reviewed information and should not silently change afterward.