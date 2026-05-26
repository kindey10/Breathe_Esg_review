# SOURCES.md

# How the fabricated data was designed

I didn’t want the sample datasets to feel random.

Before creating the ingestion files, I spent time looking at how enterprise exports from:
- SAP systems
- utility portals
- travel platforms

usually behave — especially where they tend to become messy.

The goal wasn’t to perfectly recreate production systems.

The goal was to recreate the kinds of ingestion problems ESG analyst teams actually deal with.

<br>

# SAP activity exports

## What I researched

I looked into:
- ERP export structures
- procurement CSV patterns
- fuel activity exports
- operational flat-file workflows

Common patterns:
- inconsistent units
- internal naming conventions
- vendor metadata gaps
- mixed procurement categories

<br>

## What I modeled

The prototype includes:
- fuel activity rows
- procurement records
- unusual quantities
- inconsistent units
- suspicious operational values

Examples:
- massive procurement quantities
- missing vendor names
- mixed fuel units

<br>

## What would break in production

Real SAP ingestion would also require:
- master-data mapping
- vendor normalization
- duplicate detection
- asynchronous processing
- massive file handling
- schema reconciliation

<br>

# Utility electricity exports

## What I researched

I looked into:
- utility portal exports
- electricity billing structures
- facilities reporting formats

Common patterns:
- billing-period inconsistencies
- mixed energy units
- facility-level aggregation
- incomplete metadata

<br>

## What I modeled

The prototype includes:
- electricity CSV exports
- kWh normalization
- MWh conversion
- missing facility names
- suspicious usage quantities

<br>

## Production challenges

Real utility ingestion would likely require:
- PDF parsing
- OCR
- interval meter support
- timezone handling
- utility-specific schemas

<br>

# Travel activity exports

## What I researched

I looked into:
- Concur exports
- Navan-style reports
- travel expense exports

Common patterns:
- inconsistent transport categories
- incomplete distances
- vendor naming inconsistencies
- airport/location codes

<br>

## What I modeled

The prototype includes:
- flights
- train travel
- taxi travel
- missing travel metadata
- suspicious travel distances

<br>

## Production challenges

Real travel ingestion would likely require:
- airport mapping
- geolocation enrichment
- itinerary reconciliation
- duplicate trip detection
- emissions factor linkage

<br>

# Why the sample data intentionally contains errors

Perfect datasets are unrealistic.

So I intentionally fabricated:
- invalid rows
- inconsistent units
- suspicious values
- missing metadata
- operational anomalies

because ESG ingestion workflows are usually messy before they become audit-ready.