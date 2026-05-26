# DECISIONS.md

# Why these implementation choices were made

This project intentionally prioritizes:
- ingestion realism
- operational review
- audit-style workflows

over:
- polished analytics
- complex visualization
- heavy authentication flows

<br>

# Why I used CSV uploads everywhere

CSV exports are still extremely common inside enterprise operational workflows.

I chose CSV ingestion because:
- SAP exports are commonly shared as flat files
- facilities teams export CSVs from utility portals
- travel platforms often provide spreadsheet exports
- CSVs are easy for analysts to manually validate

I intentionally avoided live API integrations because the assignment focused more on workflow quality than integration complexity.

<br>

# Why SAP data was simplified

Real SAP ecosystems are massive.

Instead of implementing:
- IDocs
- OData services
- BAPI integrations

I focused on simulating:
- operational flat-file exports
- inconsistent units
- procurement activity
- facility-linked activity rows

This kept the prototype realistic while staying manageable within assignment scope.

<br>

# Why suspicious detection exists

While reading the assignment, one thing stood out clearly:

the workflow was supposed to include analyst review.

Because of that, I intentionally added:
- outlier detection
- suspicious procurement quantities
- missing metadata checks
- unusual operational values

instead of simply validating required fields.

<br>

# Why failed rows are separated

I intentionally separated:
- ingestion failures
from:
- reviewable operational records

because enterprise systems usually treat these as completely different operational problems.

An invalid ingestion row should not pollute analyst review workflows.

<br>

# Why I kept authentication lightweight

The assignment felt more focused on:
- ingestion modeling
- review workflow
- operational architecture

than on authentication UX.

So I intentionally used:
- demo organization membership
- lightweight access flow

to reduce reviewer friction.

<br>

# Why I chose Django REST Framework

Django REST Framework works extremely well for:
- relational operational workflows
- ingestion pipelines
- structured APIs
- review systems

The assignment naturally mapped well to:
- models
- serializers
- validation layers
- operational endpoints

<br>

# Why React + Vite

The frontend needed to feel like:
- an operational review console
- not a marketing website

React made it easy to structure:
- dashboard state
- review tables
- ingestion flows
- status updates

Vite kept frontend iteration lightweight and fast.

<br>

# Why SQLite was enough here

For an assignment prototype:
- SQLite reduced setup friction
- deployment stayed simple
- reviewers can run locally easily

If this became production software, I would move to PostgreSQL immediately.

<br>

# Questions I would ask in a real product discussion

If this were a real ESG ingestion platform discussion, I would ask:
- how large are ingestion volumes?
- should uploads process asynchronously?
- should analysts approve in bulk?
- how long are source files retained?
- should rejected rows support reprocessing?
- how strict should audit locking be?
- how are emissions factors versioned?