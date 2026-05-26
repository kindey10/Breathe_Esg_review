# DECISIONS.md

# Goal

This document explains major ambiguities and implementation decisions made during the assignment.

---

# Why I Chose CSV Uploads

I chose CSV uploads for all three source types because:
- enterprise teams commonly export CSVs
- CSVs are easy for analysts to validate manually
- they simulate realistic onboarding workflows
- they are fast to prototype within assignment constraints

I intentionally did not build live API ingestion because the assignment emphasized workflow quality over integration complexity.

---

# SAP Handling Decision

SAP systems are extremely large and inconsistent.

I chose to simulate:
- flat-file SAP exports
- inconsistent units
- plant/facility codes
- procurement activity rows

instead of implementing:
- OData services
- BAPI integrations
- IDoc parsing

This kept the scope realistic for a prototype while still representing SAP complexity.

---

# Utility Data Decision

I chose utility portal CSV exports instead of PDF parsing.

Reason:
- facilities teams commonly export CSVs from utility portals
- PDF parsing would add OCR complexity without improving ingestion workflow evaluation
- the assignment focused more on normalization and analyst review

I still modeled:
- billing periods
- electricity units
- inconsistent consumption formats

---

# Travel Data Decision

I modeled travel exports similar to Concur/Navan CSV exports.

I included:
- flights
- hotels
- ground transport
- missing distances
- inconsistent categories

This allowed the workflow to simulate different travel emission categories.

---

# Why I Added Suspicious Detection

The assignment specifically mentioned:
- suspicious rows
- analyst review
- audit signoff

Because of this, I intentionally added:
- outlier quantity detection
- missing metadata checks
- suspicious procurement values

instead of simply validating required fields.

---

# Why Failed Rows Are Separate

I separated:
- failed ingestion rows
from:
- reviewable activity records

because enterprise ingestion systems usually distinguish:
- parsing failures
- analyst-reviewable operational data

Invalid rows should not pollute analyst review queues.

---

# Why I Did Not Add Full Authentication

The assignment did not focus on authentication flows.

I used:
- lightweight demo login behavior
- organization membership fallback

to reduce friction for reviewers and keep focus on ingestion workflow quality.

---

# Why I Chose React + Django REST

Django REST Framework works well for:
- structured operational APIs
- relational data models
- ingestion workflows

React works well for:
- analyst dashboards
- operational UIs
- fast review interactions

---

# Why I Used SQLite

SQLite reduced setup complexity and made deployment easier for an assignment prototype.

In production I would move to PostgreSQL.

---

# Questions I Would Ask a PM

If this were a real product discussion, I would ask:
- how large are expected ingestion volumes?
- should ingestion be async?
- how strict should audit locking be?
- should analysts be allowed bulk approvals?
- how are emission factors managed?
- should failed rows support reprocessing?
- what retention policy exists for uploaded source files?