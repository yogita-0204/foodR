# 🛒 foodR

College shop pre-order and crowd management web app.

## Overview

foodR is a Django-based platform for college users and shop owners. Students can browse shops, manage carts, place orders, and track status. Shop owners can manage menus, orders, and analytics from a dedicated dashboard.

## Live Demo

- Production app: [food-r-rouge.vercel.app](https://food-r-rouge.vercel.app/)
- Vercel deployment: [food-96cosbwc9-yogita-yadavs-projects.vercel.app](https://food-96cosbwc9-yogita-yadavs-projects.vercel.app/)
- Admin panel: [localhost/admin](http://127.0.0.1:8000/admin/)

## Features

- Role-based login for college users and shop owners
- Shop, menu, category, and order management
- Session-based cart with checkout flow
- Wallet and payment support
- Notifications for order updates
- Analytics dashboard for owners
- Responsive templates with a shared theme system

## Tech Stack

| Layer | Stack |
| --- | --- |
| Backend | Django 5.x, Python 3.10+ |
| Database | SQLite for local development |
| Frontend | Django templates, Tailwind CDN, vanilla JavaScript |
| Deployment | Vercel, WhiteNoise for static handling |

## Local Setup

1. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run migrations:

   ```bash
   python manage.py migrate
   ```

4. Create a superuser:

   ```bash
   python manage.py createsuperuser
   ```

5. Start the server:

   ```bash
   python manage.py runserver
   ```

6. Open the app:

   - Main site: [127.0.0.1:8000](http://127.0.0.1:8000/)
   - Admin panel: [127.0.0.1:8000/admin](http://127.0.0.1:8000/admin/)

## Environment Variables

Set these for deployment:

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG`
- `DJANGO_ALLOWED_HOSTS`

Optional email settings are documented in [foodR/settings.py](foodR/settings.py).

## Deployment

- Vercel config: [vercel.json](vercel.json)
- WSGI entrypoint: [api/index.py](api/index.py)
- Django settings: [foodR/settings.py](foodR/settings.py)

## Docs

- Project review: [PROJECT_REVIEW.md](PROJECT_REVIEW.md)
- Developer guide: [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)
- Admin setup: [ADMIN_SETUP_GUIDE.md](ADMIN_SETUP_GUIDE.md)
- Theme guide: [THEME_DOCUMENTATION.md](THEME_DOCUMENTATION.md)

## Notes

- SQLite is used locally.
- Media uploads live in `media/`.
- Static files are configured for development and production.

