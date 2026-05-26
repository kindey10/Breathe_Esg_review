# TRADEOFFS.md

# Goal

This document explains intentional tradeoffs and features that were deliberately not built.

---

# 1. No Real SAP/API Integrations

I intentionally did not build:
- live SAP integrations
- Concur APIs
- utility APIs

Reason:
- integration setup complexity was too large for assignment scope
- the assignment emphasized ingestion modeling and review workflow quality
- realistic CSV exports still demonstrate ingestion handling

---

# 2. No Emissions Calculation Engine

The prototype normalizes activity data but does not calculate carbon emissions.

Reason:
- the assignment focused more on ingestion and analyst review
- emission factor modeling introduces another major domain layer
- ingestion quality is upstream of emissions computation

I prioritized:
- validation
- normalization
- audit workflow

instead of carbon math.

---

# 3. No Full Authentication/Permissions System

I intentionally kept authentication lightweight.

Reason:
- reviewers should immediately access the workflow
- enterprise RBAC systems are large in scope
- assignment grading focused more on workflow modeling

I still modeled:
- organizations
- memberships
- multi-tenancy structure

to show future scalability.

---

# Additional Smaller Tradeoffs

I also intentionally did not build:
- mobile responsiveness
- advanced analytics dashboards
- PDF ingestion
- OCR pipelines
- async processing queues
- reviewer comments
- bulk approval actions
- file versioning

These were intentionally deprioritized in favor of:
- stable ingestion flow
- realistic normalization
- review workflow clarity
- deployment quality