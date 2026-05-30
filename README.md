# Campus Lost & Found

A simple Django + HTML lost-and-found management system for campus items.

## Features

- Report lost items
- Report found items
- Search and filter by status
- View item details
- Admin access for item management
- Campus email registration and verified reporter profiles
- Secure claim workflow for found items

## Setup

1. Install dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```
2. Run database migrations:
   ```bash
   python manage.py migrate
   ```
3. Start the development server:
   ```bash
   python manage.py runserver
   ```
4. Open `http://127.0.0.1:8000/` in your browser.

## Admin

Create a superuser to manage items:

```bash
python manage.py createsuperuser
```

Then open `http://127.0.0.1:8000/admin/`.
