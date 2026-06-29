# Control project system

## Overview
A Django-based **internal project monitoring system** (no public users).  
Admins create and maintain projects in **Django Admin**, can **filter by company, locations, date range**, and can **export to Excel**.  
Senior managers can **view locations on a map (Leaflet)** and query data through simple APIs (active/all locations, activity by date range, etc.).

---

## Features

### Admin & Data Entry
- Create/manage **Companies**, **Day Formats**, and **Projects**
- Strong validation in `clean()` and computed fields in `save()`:
  - `total_days`, `total_cycle`, and `is_active_now`
- **Import/Export to Excel** with `django-import-export`
- Advanced list filters with **date range** (via `django-admin-rangefilter`)
- Read-only computed fields in admin: `total_days`, `total_cycle`, `is_active_now`

### Project Tracking
- Active project detection via custom manager: `ProjectModel.active_locations`
- Inclusive day counting between `start_date` and `end_date`
- Cycle math: supports `start_cycle`/`end_cycle` (2 cycles/day)

### Manager Access (Read-Only)
- **Map integration (Leaflet)** to visualize active/all points
- **APIs** for:
  - Active locations
  - All locations
  - Company/location activity summaries in a given date range
  - Download latest project PDF (if location is active)

### Feedback Module
- Record employer **feedback per project**
- Admin **responses** with optional file attachments (e.g., ISO forms)

---

## Tech Stack
- **Backend:** Django, Django REST Framework (DRF), Django Rest Framework gis
- **Admin Tools:** django-import-export, django-admin-rangefilter
- **DB:** PostgreSQL
- **Frontend Integration:** Leaflet.js (separate frontend)
- **Storage:** Local `FileField` for PDFs and attachments

---

## How “Active Days” Are Calculated
For a given query range `[start, end]`:
- Overlap is computed with each project’s `[start_date, end_date or end]`
- If `end_date` is `NULL`, it’s treated as `end` for the overlap
- `active_days = (overlap_end - overlap_start) + 1` (inclusive)


---
## Installation & Setup
```bash
# Clone
git clone https://github.com/mbnahmadi/control-project.git
cd control-project

# Install
pip install -r requirements.txt

# Migrate
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run dev server
python manage.py runserver
```
