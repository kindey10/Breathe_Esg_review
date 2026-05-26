# SOURCES.md

# Goal

This document explains what real-world source formats were researched and how they influenced the prototype design.

---

# 1. SAP Fuel & Procurement Data

## Research

I researched:
- SAP flat-file exports
- SAP procurement CSV exports
- enterprise ERP export patterns

Common characteristics:
- inconsistent units
- internal plant codes
- procurement categories
- non-user-friendly column naming
- mixed formatting quality

---

## What I Modeled

I modeled:
- flat CSV exports
- fuel quantities
- procurement rows
- inconsistent units
- suspicious procurement values
- facility references

---

## What Would Break in Production

Real SAP deployments would also require:
- mapping tables
- master data reconciliation
- vendor normalization
- asynchronous ingestion
- duplicate detection
- extremely large files

---

# 2. Utility Electricity Data

## Research

I researched:
- utility portal exports
- electricity billing CSV structures
- facility electricity reporting

Common characteristics:
- billing periods
- kWh/MWh inconsistencies
- facility-level aggregation
- non-calendar reporting periods

---

## What I Modeled

I modeled:
- electricity CSV uploads
- usage normalization
- billing periods
- inconsistent units
- missing facility metadata

---

## What Would Break in Production

Production utility ingestion would likely require:
- PDF parsing
- OCR handling
- utility-specific schemas
- timezone handling
- demand charge parsing
- interval meter data

---

# 3. Corporate Travel Data

## Research

I researched:
- Concur exports
- Navan travel exports
- travel expense reporting formats

Common characteristics:
- multiple transport categories
- incomplete distances
- airport/location codes
- inconsistent vendor naming

---

## What I Modeled

I modeled:
- flights
- hotels
- ground transport
- inconsistent distances
- suspicious travel values

---

## What Would Break in Production

Production travel ingestion would likely require:
- airport code mapping
- geolocation enrichment
- emissions-factor mapping
- duplicate itinerary handling
- traveler reconciliation

---

# Why I Fabricated Sample Data

The assignment explicitly required creating realistic fabricated data after researching source shapes.

I intentionally designed sample datasets with:
- realistic formatting inconsistencies
- invalid rows
- suspicious quantities
- mixed units
- missing fields

because enterprise ESG ingestion data is rarely perfectly clean.