# MODEL.md

# What I optimized the data model for

I wanted the backend structure to feel closer to a real internal ESG operations system than a generic CRUD app.

So the models are organized around:
- ingestion batches
- traceability
- reviewability
- audit flow
- normalization

rather than around frontend pages.

<br>

# Core idea

The system intentionally separates:

| Layer | Responsibility |
|:--|:--|
| Raw uploaded files | Source-of-truth operational input |
| Failed ingestion rows | Parsing/validation failures |
| Standardized activity records | Operational ESG review layer |
| Analyst review state | Audit workflow layer |

This separation mirrors how enterprise ingestion pipelines are usually structured.

<br>

# Main models

## Organization

Represents a client/company using the system.

Used for:
- multi-tenancy
- data isolation
- future scalability

Example:
```text
Acme Manufacturing India Pvt Ltd
```

<br>

## Membership

Links users to organizations.

I added this because ESG workflows are usually organization-scoped rather than user-scoped.

This creates a foundation for:
- analyst roles
- reviewer permissions
- organization isolation

<br>

## DataSource

Represents where uploaded data came from.

Examples:
- SAP export
- utility portal export
- travel platform export

I intentionally separated source systems from ingestion batches because multiple uploads can belong to the same operational system.

<br>

## IngestionBatch

Represents one uploaded file.

Tracks:
- upload timestamp
- source type
- ingestion status
- failed row count
- flagged row count
- upload metadata

This acts as the operational container for ingestion tracking.

<br>

## ActivityRecord

This is the core operational model.

Represents normalized ESG activity after:
- parsing
- validation
- unit normalization

Examples:
- fuel usage
- electricity consumption
- travel activity

The model stores:
- standardized quantities
- normalized units
- activity category
- review status
- issue flags
- audit lock state

<br>

## FailedRow

Represents ingestion rows that failed before operational review.

Examples:
- invalid units
- malformed numeric values
- missing required fields
- unsupported formats

I intentionally separated failed rows from analyst review because invalid ingestion rows should not enter operational workflows.

<br>

# Multi-tenancy approach

The prototype supports organization-scoped data using:
- Organization
- Membership
- organization-linked records

This creates clean separation between enterprise clients.

<br>

# Traceability philosophy

One thing I wanted to preserve throughout the workflow:

every operational record should be traceable back to its source.

So every activity record can be connected back to:
- upload batch
- source system
- upload timestamp
- original source file

This becomes extremely important in audit workflows.

<br>

# Unit normalization

Operational ESG data often arrives with inconsistent units.

Examples:
- gallons
- liters
- MWh
- kWh

I normalized quantities into standard operational units so downstream workflows can operate consistently.

<br>

# Review workflow design

Records move through:
- APPROVED
- FLAGGED
- REJECTED

Approved rows become locked to simulate audit-ready records.

Flagged rows intentionally require analyst review before signoff.

<br>

# Why I avoided a raw JSON-only approach

A JSON-heavy structure would have been faster initially.

But it becomes harder to:
- validate consistently
- review operationally
- normalize cleanly
- filter reliably
- audit later

I chose structured normalized models because the assignment focused heavily on operational review workflows.

<br>

# If this became production software

I would likely add:
- PostgreSQL
- async ingestion queues
- object storage
- event-driven processing
- schema versioning
- duplicate detection
- reviewer audit history