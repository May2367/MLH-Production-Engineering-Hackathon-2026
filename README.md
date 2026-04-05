## URL Shortener API

A REST API for creating and managing shortened URLs, built with Flask, Peewee ORM, and PostgreSQL.

## Architecture
┌─────────┐     HTTP      ┌───────────┐     Peewee ORM     ┌────────────┐
│ Client  │ ────────────▶ │   Flask   │ ─────────────────▶ │ PostgreSQL │
│ (curl/  │ ◀──────────── │    App    │ ◀───────────────── │            │
│ browser)│   JSON/302    └───────────┘                     └────────────┘
│
│ logs to
▼
stdout (JSON)
**Components:**
- **Client** — anything making HTTP requests (browser, curl, another service)
- **Flask** — receives requests, runs route logic, returns JSON responses
- **Peewee ORM** — translates Python model operations into SQL queries
- **PostgreSQL** — stores users, URLs, and events persistently
- **JSON logging** — every request is logged as structured JSON to stdout

## Prerequisites

- Python 3.13+
- PostgreSQL running locally
- uv (Python package manager)

Install uv:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Setup
```bash
1. Clone the repo
git clone https://github.com/May2367/MLH-Production-Engineering-Hackathon-2026.git
cd MLH-Production-Engineering-Hackathon-2026

2. Install dependencies
uv sync

3. Start PostgreSQL
sudo service postgresql start

4. Create the database
sudo -u postgres createdb hackathon_db

5. Configure environment
cp .env.example .env

6. Load seed data
uv run load_data.py

7. Start the server
uv run run.py
```

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| FLASK_DEBUG | false | Enable debug mode (set to false in production) |
| DATABASE_NAME | hackathon_db | PostgreSQL database name |
| DATABASE_HOST | localhost | Database host |
| DATABASE_PORT | 5432 | Database port |
| DATABASE_USER | postgres | Database user |
| DATABASE_PASSWORD | postgres | Database password |

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | /health | Health check — returns 200 if app is running |
| GET | /metrics | CPU, memory, and disk usage stats |
| GET | /urls | List all shortened URLs |
| GET | /urls/<id> | Get a single URL by ID |
| POST | /urls | Create a new shortened URL |
| GET | /<short_code> | Redirect to the original URL |
| GET | /users | List all users |
| GET | /users/<id> | Get a single user by ID |
| GET | /events | List all events |
| GET | /events/<id> | Get a single event by ID |

### POST /urls — Example Request
```bash
curl -X POST http://127.0.0.1:5000/urls \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "short_code": "abc123", "original_url": "https://example.com"}'
```

## Running Tests
```bash
# Run tests
uv run pytest tests/ -v

# Run with coverage report
uv run pytest tests/ -v --cov=app --cov-report=term-missing
```

## Troubleshooting

**`createdb: command not found`**
PostgreSQL CLI tools aren't in your PATH. Install with:
```bash
sudo apt install postgresql postgresql-client
```

**`password authentication failed for user "postgres"`**
Set the postgres user password to match your .env:
```bash
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'postgres';"
```

**`relation "url" does not exist`**
Tables haven't been created yet. Run:
```bash
uv run load_data.py
```

**Port 5000 already in use**
Another process is using the port. Find and kill it:
```bash
sudo lsof -i :5000
kill -9 <PID>
```