# AEGIS campusOS

Unified campus platform that combines governance, academics, opportunities, and student interaction in one dashboard.

## Highlights

- Role-based portals: Admin, Faculty, Student, Authority
- Academic management: courses, sessions, attendance, results, course notes
- Grievance desk: tracking, escalation, resolution workflow
- Opportunities: internships, applications, review workflows
- Community: ride sharing, lost and found, course forum
- Admissions and fee management modules

## Roles and Access

- Admin: full management of users, courses, sessions, admissions, internships, fees
- Faculty: attendance, results, course notes, community moderation
- Student: attendance, results, leaves, feedback, community participation
- Authority: grievance desk ownership and resolution

## Community Scope

- If a student has an assigned course, community feeds show both course-specific and campus-wide posts.
- If a student has no course, posts are created in the campus-wide scope.

## Tech Stack

- Backend: Django 3.1.1
- Frontend: HTML, CSS, JavaScript, Bootstrap
- Database: SQLite (dev) / PostgreSQL (production)
- Deployment: Gunicorn + WhiteNoise

## Getting Started

### Prerequisites

- Python 3.10+ recommended
- Virtual environment tooling (venv, virtualenv)

### Setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000 in your browser.

### Optional Seed Data

```bash
python manage.py seed_users
```

## Environment Variables

The app uses these environment variables (all optional for local dev):

- `SECRET_KEY`: Django secret key
- `DEBUG`: `True` or `False`
- `ALLOWED_HOSTS`: comma-separated list (ex: `localhost,127.0.0.1`)
- `DATABASE_URL`: PostgreSQL URL for production
- `RECAPTCHA_SITE_KEY` and `RECAPTCHA_SECRET_KEY`: reCAPTCHA keys
- `DEMO_LOGIN_ENABLED`: `True` or `False`
- `DEMO_LOGIN_EMAIL`: demo login email

## Static and Media

- Static files are served from `STATIC_URL=/static/` with WhiteNoise.
- Uploads are stored in `MEDIA_ROOT=media/` and served from `MEDIA_URL=/media/`.

If deploying to production, run:

```bash
python manage.py collectstatic
```

## Project Structure

- `college_management_system/`: Django project settings and URLs
- `main_app/`: core app (models, views, templates, static assets)
- `main_app/templates/`: role-based templates
- `main_app/static/`: CSS, images, JS
- `db.sqlite3`: local development database

## Common Tasks

### Create Admin User

```bash
python manage.py createsuperuser
```

### Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Run Server

```bash
python manage.py runserver
```

## Troubleshooting

- If static assets do not load in production, ensure `collectstatic` has been run and `DEBUG=False`.
- If a student or faculty lacks a course/session, Admin should assign it in Manage Students or Manage Faculty.

## License

This project is provided as-is for internal campus use and customization.
