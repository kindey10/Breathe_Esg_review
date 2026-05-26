# Breathe ESG Review Workflow

A lightweight ESG data ingestion and review workflow prototype inspired by enterprise sustainability reporting systems.

Built for the Breathe ESG assignment.

---

# Features

- Multi-source ESG data ingestion
- Standardized activity record generation
- Unit normalization
- Validation and issue detection
- Analyst review workflow
- Failed row separation
- Auto-seeded demo datasets
- React dashboard UI
- Django REST backend

---

# Supported Upload Types

| Source | Example |
|---|---|
| SAP Activity CSV | Fuel + procurement |
| Utility Electricity CSV | Energy consumption |
| Travel Activity CSV | Business travel |

---

# Workflow

1. Upload ESG source CSV
2. Parse and validate rows
3. Normalize units into standard ESG records
4. Flag suspicious/outlier values
5. Review approved/flagged records
6. Separate failed ingestion rows

---

# Demo Screenshots

## Overview Dashboard

![Overview](screenshots/overview.png)

---

## Review Records

![Review](screenshots/review-records.png)

---

## Failed Rows

![Failed](screenshots/failed-rows.png)

---

## Upload Workflow

![Upload](screenshots/upload-workflow.png)

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

---

# Local Setup

## Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

---

## Frontend

```bash
cd frontend
npm install
npm run dev
```

---

# Demo Credentials

```txt
Username: kindey
Password: Demo@12345
```

---

# Notes

- Demo data is automatically seeded using `seed_demo`
- Failed rows are intentionally separated from reviewable records
- Suspicious records are flagged for analyst review
- Clean records are automatically approved and locked