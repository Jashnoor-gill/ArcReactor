## AEGIS campusOS

Unified campus platform that combines governance, academics, opportunities, and student interaction in one dashboard.

### Core Modules

- Role-based authentication (Student, Faculty, Authority, Admin)
- Grievance management with tracking and escalation
- Academic resource and course tracking
- Internship and research opportunity portal

### Tech Stack

- Backend: Django
- Frontend: HTML, CSS, JavaScript, Bootstrap
- Database: SQLite (dev) / PostgreSQL (prod-ready)

### Local Setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open `http://127.0.0.1:8000` in your browser.
