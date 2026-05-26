# Breathe ESG Review Workflow

A lightweight enterprise-style ESG data ingestion and review workflow prototype inspired by real sustainability reporting systems.

Built as part of the Breathe ESG assignment.

---

# Live Demo

Frontend:
https://breathe-esg-review.vercel.app

Backend API:
https://breathe-esg-review-6gh7.onrender.com/api/ingestion/dashboard/

---

# Project Overview

This project simulates how enterprise ESG platforms ingest, standardize, validate, review and approve sustainability activity data before it becomes audit-ready evidence.

The workflow focuses on:

- ESG source data ingestion
- Unit normalization
- Validation and anomaly detection
- Analyst review workflow
- Failed row separation
- Audit-style review pipeline

The application is intentionally designed like an internal enterprise operations console rather than a generic student CRUD dashboard.

---

# Key Features

## Multi-source ESG data ingestion

Supports CSV uploads from:

- SAP activity exports
- Utility electricity data
- Corporate travel activity data

---

## Standardization Engine

Raw uploaded data is normalized into standardized ESG activity records.

Examples:

| Raw Input | Standardized Output |
|---|---|
| 20 US_GAL petrol | 75.708 L |
| 3 MWh electricity | 3000 kWh |
| Travel entries | standardized km values |

---

## Validation & Issue Detection

The system automatically detects:

- Missing fields
- Invalid numeric values
- Unsupported units
- Negative quantities
- Outlier values
- Missing vendor/facility information
- Suspicious procurement values

---

## Analyst Review Workflow

Records are categorized into:

| Status | Meaning |
|---|---|
| APPROVED | Clean records auto-approved |
| FLAGGED | Suspicious records requiring analyst review |
| FAILED | Invalid ingestion rows rejected before standardization |
| REJECTED | Manually rejected by reviewer |

---

## Failed Row Separation

Invalid source rows are separated from reviewable activity records to simulate enterprise ingestion pipelines.

---

## Auto-seeded Demo Data

The project automatically seeds realistic demo datasets using:

```bash
python manage.py seed_demo
```

This allows reviewers to immediately test the application without manually uploading files.

---

# Supported Upload Types

| Dataset Type | Description |
|---|---|
| SAP Activity | Fuel + procurement ESG activity data |
| Utility Electricity | Scope 2 electricity consumption |
| Travel Activity | Employee business travel data |

---

# Workflow

1. Upload ESG source CSV
2. Parse source rows
3. Validate records
4. Normalize into standardized ESG activity records
5. Flag suspicious/outlier values
6. Review flagged records
7. Approve/reject records
8. Separate failed ingestion rows

---

# Dashboard Metrics

| Metric | Meaning |
|---|---|
| Source Rows | Total uploaded raw rows |
| Reviewable | Successfully standardized activity records |
| Approved | Clean records auto-approved |
| Flagged | Records requiring analyst review |
| Failed | Invalid ingestion rows |

---

# UI Design

The frontend uses a clean bento-style operational dashboard layout inspired by enterprise review consoles.

Design goals:
- clean review workflow
- low visual clutter
- analyst-friendly layout
- operational console feel
- fast readability

---

# Screenshots

## Overview Dashboard

![Overview](./screenshots/overview.png)

---

## Review Records

![Review Records](./screenshots/review-records.png)

---

## Failed Rows

![Failed Rows](./screenshots/failed-rows.png)

---

## Upload Workflow

![Upload Workflow](./screenshots/upload-workflow.png)

---

# Tech Stack

## Frontend

- React
- Vite
- CSS

## Backend

- Django
- Django REST Framework
- SQLite

## Deployment

- Frontend hosted on Vercel
- Backend hosted on Render

---

# Local Setup

## Clone Repository

```bash
git clone https://github.com/kindey10/Breathe_Esg_review.git
cd Breathe_Esg_review
```

---

# Backend Setup

```bash
cd backend

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt

python manage.py migrate

python manage.py seed_demo

python manage.py runserver
```

Backend runs on:

```txt
http://127.0.0.1:8000
```

---

# Frontend Setup

```bash
cd frontend

npm install

npm run dev
```

Frontend runs on:

```txt
http://localhost:5173
```

---

# Demo Credentials

```txt
Username: kindey
Password: Demo@12345
```

---

# Notes

- Demo datasets are automatically seeded during setup
- Suspicious records are intentionally flagged for analyst review
- Failed rows are separated from standardized reviewable records
- Clean records are automatically approved
- Backend is hosted on Render free tier and may take ~30 seconds to wake on first request

---

# Device Support

This project is currently optimized for:

- laptops
- desktop browsers

The UI is not fully mobile responsive because the workflow is designed primarily as an enterprise review console.

---

# Future Improvements

Possible future enhancements:

- audit timeline UI
- authentication screens
- charts & ESG analytics
- downloadable reports
- advanced filtering/search
- reviewer comments
- cloud storage integration

---

# Author

Kinjal Pandey

GitHub:
https://github.com/kindey10
