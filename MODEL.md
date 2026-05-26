# MODEL.md

## Goal

The system ingests ESG-related source data from multiple enterprise systems, normalizes it into a standardized structure and allows analysts to review records before they become audit-ready.

---

# Core Design Philosophy

I designed the data model around the ingestion workflow rather than around UI screens.

The focus was:
- traceability
- normalization
- reviewability
- audit readiness

The app separates:
- raw uploaded source rows
- normalized activity records
- failed ingestion rows
- analyst review decisions

This mirrors how enterprise ESG pipelines are usually structured.

---

# Main Models

## Organization

Represents a client company.

Used for:
- multi-tenancy
- data isolation
- future scalability

Example:
- Acme Manufacturing India Pvt Ltd

---

## Membership

Links users to organizations.

This allows:
- organization-scoped access
- future role expansion
- analyst separation

---

## DataSource

Represents the origin of uploaded ESG data.

Examples:
- SAP export
- Utility portal CSV
- Travel platform export

I separated this from ingestion batches so multiple uploads can belong to the same source system.

---

## IngestionBatch

Represents a single uploaded file.

Tracks:
- upload timestamp
- dataset type
- upload status
- source file
- failed rows
- flagged rows

This acts as the source-of-truth container for uploaded data.

---

## ActivityRecord

Represents normalized ESG activity data after parsing and validation.

Examples:
- diesel fuel consumption
- electricity usage
- travel distance

This model stores:
- normalized quantity
- normalized units
- activity category
- issue flags
- review status
- audit lock state

This is the central operational model in the system.

---

## FailedRow

Represents ingestion rows that failed validation before normalization.

Examples:
- invalid units
- missing quantity
- malformed dates
- unsupported formats

I intentionally separated failed rows from reviewable records because failed ingestion data should not enter the analyst workflow.

---

# Multi-tenancy

The system supports multi-tenancy through:
- Organization model
- Membership model
- organization-linked records

This ensures data isolation between enterprise clients.

---

# Source-of-truth Tracking

Every activity record can be traced back to:
- source system
- ingestion batch
- upload timestamp
- original uploaded file

This is important for auditability and enterprise ESG workflows.

---

# Unit Normalization

The system standardizes inconsistent units into normalized operational units.

Examples:
- MWh → kWh
- gallons → liters

This allows downstream review and future emissions calculations to operate consistently.

---

# Audit Workflow

Records move through:
- APPROVED
- FLAGGED
- REJECTED

Approved records are locked to simulate audit-ready workflows.

---

# Why I Did Not Store Raw JSON Everywhere

A raw JSON-only structure would have been faster initially but harder to:
- validate
- review
- filter
- audit
- normalize consistently

I chose structured normalized models because analyst workflows were central to the assignment.

---

# Scalability Considerations

The current prototype uses SQLite for simplicity.

In production I would likely:
- move to PostgreSQL
- add async ingestion workers
- add event-driven processing
- add object storage for uploaded files