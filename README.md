# 📚 Local Library

A Django-based web application for managing a small local library. Users can browse books and authors, manage borrowing, and librarians can track loans and renewals.

---

## ✨ Features

- Browse books and authors with paginated list and detail views
- User authentication (login, logout, password reset)
- Book borrowing management — users see their own loans
- Librarians can renew borrowed books
- Staff can view all active loans
- Admin interface for full CRUD management
- PostgreSQL (production) and SQLite (development) support

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) — modern Python package manager
- Docker & Docker Compose (for containerized setup)

---

### Option 1 — Local Dev with UV (SQLite)

```bash
# 1. Clone and enter the repo
git clone https://github.com/adityaiitg/Local-Library.git
cd Local-Library

# 2. Install dependencies
uv sync

# 3. Create your .env file
cp .env.example .env
# Edit .env — generate a SECRET_KEY:
uv run python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# 4. Run migrations & create a superuser
uv run python manage.py migrate
uv run python manage.py createsuperuser

# 5. Start the development server
uv run python manage.py runserver
```

Open http://127.0.0.1:8000 in your browser.

---

### Option 2 — Docker with SQLite (dev override)

```bash
# Build and start (uses docker-compose.override.yml automatically)
docker compose up --build

# In a separate terminal, run migrations
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

Open http://localhost:8000

---

### Option 3 — Docker with PostgreSQL (production-like)

```bash
# 1. Set up your .env
cp .env.example .env
# Edit .env with your values

# 2. Launch with the full stack (web + postgres)
docker compose -f docker-compose.yml up --build

# 3. Run migrations
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

Open http://localhost:8000

---

## 🧪 Running Tests

```bash
# Run all tests
uv run pytest -v

# Run with coverage report
uv run coverage run -m pytest
uv run coverage report -m

# Run specific test file
uv run pytest catalog/tests/test_models.py -v
uv run pytest catalog/tests/test_views.py -v
uv run pytest catalog/tests/test_forms.py -v
```

---

## ⚙️ Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `SECRET_KEY` | ✅ | — | Django secret key |
| `DEBUG` | ❌ | `False` | Enable debug mode |
| `ALLOWED_HOSTS` | ❌ | `localhost,127.0.0.1` | Comma-separated list of allowed hosts |
| `DATABASE_URL` | ❌ | `sqlite:///db.sqlite3` | Database connection URL |
| `POSTGRES_DB` | ❌ | `locallibrary` | PostgreSQL database name (Docker only) |
| `POSTGRES_USER` | ❌ | `postgres` | PostgreSQL user (Docker only) |
| `POSTGRES_PASSWORD` | ❌ | `postgres` | PostgreSQL password (Docker only) |

**Database URL formats:**
```
# SQLite (local dev)
DATABASE_URL=sqlite:///db.sqlite3

# PostgreSQL
DATABASE_URL=postgres://USER:PASSWORD@HOST:5432/DBNAME
```

---

## 📁 Project Structure

```
Local-Library/
├── locallibrary/           # Django project configuration
│   ├── settings.py         # Settings (env-var driven)
│   ├── urls.py             # Root URL configuration
│   └── wsgi.py
├── catalog/                # Main application
│   ├── models.py           # Book, Author, BookInstance, Genre, Language
│   ├── views.py            # All views (list, detail, CRUD, loan management)
│   ├── forms.py            # RenewBookForm
│   ├── admin.py            # Admin configuration
│   ├── urls.py             # App URL patterns
│   ├── templates/          # HTML templates
│   └── tests/
│       ├── test_models.py  # Model unit tests
│       ├── test_views.py   # View integration tests
│       └── test_forms.py   # Form validation tests
├── templates/              # Auth templates (login, password reset)
├── Dockerfile              # Multi-stage Docker build
├── docker-compose.yml      # Production: web + PostgreSQL
├── docker-compose.override.yml  # Dev: SQLite, live reload
├── entrypoint.sh           # Docker entrypoint (wait for DB, migrate)
├── pyproject.toml          # UV package management & tool config
├── .env.example            # Environment variable template
└── manage.py
```

---

## 🛡️ Permissions

| Role | Permissions |
|---|---|
| Anonymous | None (redirected to login) |
| Authenticated User | Browse books/authors, view own loans |
| Librarian (`can_mark_returned`) | All above + view all loans + renew books |
| Staff | Admin interface access |

---

## 🐳 Docker Notes

- The `docker-compose.yml` starts **web + PostgreSQL** services
- PostgreSQL data is persisted in a named volume (`postgres_data`)
- The entrypoint script automatically waits for the DB and runs migrations
- For local development, `docker-compose.override.yml` is automatically applied, using SQLite and mounting source code for live reload
- Run with only PostgreSQL (no override): `docker compose -f docker-compose.yml up`

---

## 📊 Models

![Local Library UML](https://raw.githubusercontent.com/mdn/django-locallibrary-tutorial/master/catalog/static/images/local_library_model_uml.png)

---

## 🙏 Acknowledgements

Based on the [MDN Django Tutorial](https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Tutorial_local_library_website) — extended with UV package management, PostgreSQL support, Docker setup, and comprehensive tests.
