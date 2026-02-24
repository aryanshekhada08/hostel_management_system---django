# Hostel Management System

A Django-based hostel management system covering student onboarding, room allocation, fee tracking, wallets, complaints, notifications, and admin dashboards.

## Features
- Student and admin accounts with custom authentication
- Admissions workflow and document uploads
- Room allocation and student room dashboard
- Fee management and payment history
- Wallets with admin add/deduct flows
- Complaints and notifications
- Admin and student dashboards

## Tech Stack
- Django 5.2
- PostgreSQL
- django-tailwind + Tailwind CSS
- django-browser-reload

## Project Structure
- `apps/` local Django apps (accounts, admissions, rooms, fees, wallets, complaints, notifications)
- `config/` project settings and URLs
- `templates/` shared HTML templates
- `static/` static assets
- `theme/` Tailwind app and build assets
- `media/` uploaded files

## Setup
1. Create and activate a virtual environment.
2. Install Python dependencies.

```powershell
pip install -r requirements.txt
```

3. Configure the database in `config/settings.py` to match your local PostgreSQL credentials.

4. Apply migrations.

```powershell
python manage.py migrate
```

5. (Optional) Load sample data.

```powershell
python manage.py loaddata data.json
```

6. Create an admin user.

```powershell
python manage.py createsuperuser
```

7. Run the development server.

```powershell
python manage.py runserver
```

## Tailwind (Optional for live rebuild)
This project uses `django-tailwind`. If you want live Tailwind rebuilds:

```powershell
python manage.py tailwind install
python manage.py tailwind start
```

The configured npm path is `C:\Program Files\nodejs\npm.cmd` in `config/settings.py`. Update it if needed.

## Tests

```powershell
python manage.py test
```

## Notes
- `AUTH_USER_MODEL` is set to a custom user model in `apps.accounts`.
- Email settings are read from environment variables in `config/settings.py`. Use a `.env` file or your process manager to set them for production.
