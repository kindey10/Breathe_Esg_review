# TRADEOFFS.md

# What I intentionally did NOT build

Every useful prototype leaves something out intentionally.

This document explains the shortcuts I consciously took, what I optimized for during the assignment, and what I would change if the system evolved into a production platform.

<br>

# No live SAP/API integrations

I intentionally did not build:
- SAP APIs
- utility APIs
- travel platform integrations

Reason:
the assignment seemed more focused on:
- ingestion workflows
- normalization
- operational review
- suspicious detection

rather than on integration infrastructure.

CSV exports still simulate real ingestion challenges surprisingly well.

<br>

# No emissions calculation engine

The prototype normalizes operational ESG data but does not calculate carbon emissions.

I intentionally prioritized:
- ingestion quality
- validation
- reviewability
- audit flow

because emissions calculations depend heavily on:
- factor libraries
- methodologies
- geography
- reporting standards

That becomes an entirely separate domain layer.

<br>

# No heavy authentication system

I intentionally avoided:
- OAuth
- RBAC dashboards
- invitation flows
- enterprise auth layers

Reason:
the assignment seemed more interested in:
- operational workflow thinking
- ingestion modeling
- review logic

I still modeled:
- organizations
- memberships
- tenant separation

so the architecture can scale later.

<br>

# No async ingestion workers

Uploads process synchronously right now.

For assignment-scale datasets, this keeps the system:
- simpler
- easier to understand
- easier to deploy

In production, ingestion would likely move to:
- Celery workers
- background queues
- event-driven processing

<br>

# No mobile-first UI

The interface is intentionally optimized for:
- laptops
- desktop analyst workflows

I treated this more like:
```text
internal operational software
```

than:
```text
consumer mobile product
```

<br>

# Smaller things I intentionally deprioritized

I also intentionally skipped:
- PDF parsing
- OCR
- advanced charts
- reviewer comments
- bulk approval actions
- file versioning
- audit timelines
- emissions dashboards

I prioritized:
- stable ingestion flow
- realistic validation
- operational review clarity
- deployment quality