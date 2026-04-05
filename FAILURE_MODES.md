# Failure Modes & Recovery Guide

This document describes known failure modes for the URL Shortener API, what happens when they occur, and how to recover.

---

## 1. Database Connection Failure

What happens:
The app starts but all API endpoints return 500 errors. Logs will show:
{"level": "ERROR", "message": "server error", "error": "could not connect to server"}

Cause:
PostgreSQL is not running, or the credentials in .env are wrong.

How to fix:
    sudo service postgresql status
    sudo service postgresql start
    sudo -u postgres psql -d hackathon_db -c "SELECT 1;"

---

## 2. Database Tables Missing

What happens:
App starts successfully but all endpoints return 500. Logs show: relation "url" does not exist

Cause:
Tables were never created, or were dropped without being recreated. This happened during development when load_data.py dropped tables and the process was interrupted before recreating them.

How to fix:
    uv run load_data.py

---

## 3. Duplicate Data in Seed Files

What happens:
load_data.py crashes with: peewee.IntegrityError: duplicate key value violates unique constraint

Cause:
The seed CSV files contained duplicate usernames. Discovered during initial loading — users.csv had 2 duplicate usernames: brisknetwork23 and mellowanchor58.

How to fix:
The loader uses on_conflict_ignore() to skip duplicates silently. Verify all insert calls include this:
    Model.insert_many(batch).on_conflict_ignore().execute()

---

## 4. Foreign Key Violations During Data Load

What happens:
load_data.py crashes with: foreign key constraint violation on table "url"

Cause:
A URL or Event references a user_id that does not exist in the user table. Happens when duplicate users are skipped but their associated URLs still reference the skipped ID.

How to fix:
The loader remaps orphaned user_id values to the surviving duplicate's ID before inserting. See load_urls() in load_data.py for the remapping logic.

---

## 5. Port Already In Use

What happens:
OSError: [Errno 98] Address already in use

Cause:
Another process is using port 5000, or a previous Flask instance did not shut down cleanly.

How to fix:
    sudo lsof -i :5000
    kill -9 <PID>
    uv run run.py

---

## 6. App Process Crashes

What happens:
The server stops responding. All requests time out.

Cause:
Unhandled exception, out of memory, or the process was killed.

How to recover manually:
    uv run run.py

How to recover automatically using systemd:
Create /etc/systemd/system/urlshortener.service with this content:

    [Unit]
    Description=URL Shortener API
    After=network.target postgresql.service

    [Service]
    WorkingDirectory=/home/may/MLH_Hack/PE_Template
    ExecStart=/home/may/MLH_Hack/PE_Template/.venv/bin/python run.py
    Restart=always
    RestartSec=5

    [Install]
    WantedBy=multi-user.target

Then run:
    sudo systemctl daemon-reload
    sudo systemctl enable urlshortener
    sudo systemctl start urlshortener

The app will restart automatically within 5 seconds of any crash.

---

## 7. Slow Response Times Under Load

What happens:
Requests take 2-9 seconds under 50 concurrent users.

Cause:
List endpoints return all rows with no pagination. GET /urls returns all 2000 URLs in one response. GET /users returns all 398 users. Under concurrent load these endpoints saturate the database connection.

Identified during Locust load test with 50 users over 30 seconds:
    GET /users p95: 8,500ms
    GET /urls avg: 2,172ms
    Single record lookups like GET /urls/1: 90-500ms (fast)

How to fix:
Add pagination to list endpoints or add Redis caching for frequently requested data.

---

## 8. Environment Variables Missing

What happens:
App crashes on startup with a database connection error.

Cause:
.env file is missing. Happens after a fresh clone if the developer forgets to copy .env.example.

How to fix:
    cp .env.example .env

Required variables:
    FLASK_DEBUG     — set to false in production
    DATABASE_NAME   — PostgreSQL database name
    DATABASE_HOST   — usually localhost
    DATABASE_PORT   — usually 5432
    DATABASE_USER   — PostgreSQL username
    DATABASE_PASSWORD — PostgreSQL password

---

## Quick Reference

Error                          | Cause                      | Fix
relation does not exist        | Tables missing             | uv run load_data.py
could not connect to server    | PostgreSQL down            | sudo service postgresql start
duplicate key value            | Duplicate seed data        | Use on_conflict_ignore()
foreign key violation          | Load order wrong           | Load users before urls before events
Address already in use         | Port 5000 taken            | kill -9 $(lsof -t -i:5000)
ModuleNotFoundError            | Wrong import name          | Check filename matches import exactly
404 on all routes              | Blueprints not registered  | Check app/routes/__init__.py
All routes 500                 | DB connection failed       | Check .env and PostgreSQL status
