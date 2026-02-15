# AEGIS campusOS

Unified campus platform that combines governance, academics, opportunities, and student interaction in one dashboard.

Deployed at: https://aegis-campusos.onrender.com

## Demo Credentials

### Admin
- **adminx@aegis.local** / `xyz`

### Authority
- **authorityx@aegis.local** / `xyz`
- **hostel@aegis.local** / `hostelxyz`
- **infra@aegis.local** / `infraxyz`
- **mess@aegis.local** / `messxyz`
- **academic@aegis.local** / `acadxyz`

### Faculty
- **facultyx@aegis.local** / `xyz`
- **indu@aegis.local** / `Induxyz`
- **rohit@aegis.local** / `Rohitxyz`
- **sanju@aegis.local** / `Sanjuxyz`
- **kapil@aegis.local** / `Kapilxyz`

### Students
- **studentx@aegis.local** / `xyz`
- **tony@aegis.local** / `Tonyxyz`
- **thor@aegis.local** / `thorxyz`
- **natasha@aegis.local** / `Natashaxyz`
- **strange@aegis.local** / `Strangexyz`
- **wanda@aegis.local** / `Wandaxyz`

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

## Quality and Architecture

- Code cleanliness: modular Django apps, role-based views, reusable form templates, and consistent styling layers.
- Database schema design: relational models with explicit foreign keys, choice fields for enums, and normalized core entities.
- Security protocols: Django authentication, CSRF protection, hashed passwords, and role-based access control.
- Scalability considerations: PostgreSQL support, stateless app design, and static asset handling via WhiteNoise.
- Documentation quality: detailed README, environment variable guidance, and setup instructions.

## Tightening Checklist (No Behavior Changes)

These are non-breaking steps to improve quality without changing runtime behavior:

- Code cleanliness: add more focused docstrings, remove unused imports, and keep view logic cohesive.
- Schema design: document required fields and constraints; review nullability and indexes before tightening.
- Security: keep `DEBUG=False` in production, confirm secure cookies and allowed hosts in deployment settings.
- Scalability: prefer pagination on large lists and use database indexes on high-traffic lookups.
- Documentation: expand deployment notes and operational runbooks as the system grows.

## Product Pillars (Current Assessment)

Core pillars implemented:

- Role-based access (Admin, Faculty, Student, Authority)
- Academic workflows (courses, sessions, attendance, results, notes)
- Governance (grievance desk with tracking and escalation)
- Opportunities and internships (posting, applications, review)
- Student community (ride sharing, lost and found, forum)
- Admissions and fee management modules

Bonus pillars implemented:

- Authority role with grievance desk ownership
- Course enrollment request approvals
- Campus-wide community fallback for unassigned students
- Course notes/references for faculty
- Internship application management and status updates

Quality signals (current):

- UI/UX quality: consistent visual system and navigation, but accessibility can be improved.
- Responsiveness: works across breakpoints; long tables could benefit from pagination and better mobile patterns.
- Accessibility: needs ARIA labels and contrast checks in some views.
- Smoothness: generally stable; more loading states and empty-state guidance would help.
- Initiative and creativity: strong set of thoughtful modules; scope can expand with analytics and audit logs.
- Technical cleverness: solid Django patterns; further optimizations (caching, indexing, async tasks) remain.

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
