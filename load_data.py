import csv
from peewee import chunked
from app import create_app
from app.database import db
from app.models.user import User
from app.models.url import Url
from app.models.events import Event

app = create_app()

def load_users():
    with open('data/users.csv', newline='') as f:
        rows = list(csv.DictReader(f))
    
    with db.atomic():
        for batch in chunked(rows, 100):
            User.insert_many(batch).on_conflict_ignore().execute()

        print(f"Loaded {len(rows)} users.")

def load_urls():
    with open('data/urls.csv', newline='') as f:
        rows = list(csv.DictReader(f))

    valid_user_ids = {str(u.id) for u in User.select(User.id)}

    user_id_to_username = {}
    with open('data/users.csv', newline='') as f:
        for row in csv.DictReader(f):
            user_id_to_username[row['id']] = row['username']

    username_to_valid_id = {}
    for u in User.select(User.id, User.username):
        username_to_valid_id[u.username] = str(u.id)

    for r in rows:
        r['is_active'] = r['is_active'] == 'True'

        if r['user_id'] not in valid_user_ids:
            username = user_id_to_username.get(r['user_id'])
            if username and username in username_to_valid_id:
                r['user_id'] = username_to_valid_id[username]

    with db.atomic():
        for batch in chunked(rows, 100):
            Url.insert_many(batch).on_conflict_ignore().execute()

    print(f"Loaded {len(rows)} urls.")

def load_events():
    with open('data/events.csv', newline='') as f:
        rows = list(csv.DictReader(f))

    valid_user_ids = {str(u.id) for u in User.select(User.id)}

    id_to_username = {}
    with open('data/users.csv', newline='') as f:
        for row in csv.DictReader(f):
            id_to_username[row['id']] = row['username']

    username_to_valid_id = {}
    for u in User.select(User.id, User.username):
        username_to_valid_id[u.username] = str(u.id)

    for r in rows:
        if r['user_id'] not in valid_user_ids:
            username = id_to_username.get(r['user_id'])
            if username and username in username_to_valid_id:
                r['user_id'] = username_to_valid_id[username]

    with db.atomic():
        for batch in chunked(rows, 100):
            Event.insert_many(batch).on_conflict_ignore().execute()

    print(f"Loaded {len(rows)} events.")

with app.app_context():
    db.connect(reuse_if_open=True)

    db.execute_sql('DROP TABLE IF EXISTS "event" CASCADE;')
    db.execute_sql('DROP TABLE IF EXISTS "url" CASCADE;')
    db.execute_sql('DROP TABLE IF EXISTS "user" CASCADE;')
    db.create_tables([User, Url, Event], safe=True)

    load_users()
    load_urls()
    load_events()
