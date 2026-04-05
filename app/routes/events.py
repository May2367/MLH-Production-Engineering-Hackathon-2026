import csv
import json
from datetime import datetime
from flask import Blueprint, jsonify, request
from playhouse.shortcuts import model_to_dict
from app.models.events import Event
from app.database import db

events_bp = Blueprint("events", __name__)


@events_bp.route("/events", methods=["GET"])
def list_events():
    query = Event.select()

    url_id = request.args.get("url_id")
    if url_id:
        query = query.where(Event.url == int(url_id))

    user_id = request.args.get("user_id")
    if user_id:
        query = query.where(Event.user == int(user_id))

    event_type = request.args.get("event_type")
    if event_type:
        query = query.where(Event.event_type == event_type)

    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 50))
    query = query.paginate(page, per_page)

    return jsonify([model_to_dict(e) for e in query])


@events_bp.route("/events/<int:event_id>", methods=["GET"])
def get_event(event_id):
    try:
        event = Event.get_by_id(event_id)
        return jsonify(model_to_dict(event))
    except Event.DoesNotExist:
        return jsonify({"error": "Event not found"}), 404


@events_bp.route("/events", methods=["POST"])
def create_event():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    required = ["url_id", "user_id", "event_type"]
    for field in required:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    try:
        details = data.get("details")
        if isinstance(details, dict):
            details = json.dumps(details)

        event = Event.create(
            url_id=data["url_id"],
            user_id=data["user_id"],
            event_type=data["event_type"],
            timestamp=data.get("timestamp", datetime.utcnow()),
            details=details
        )
        return jsonify(model_to_dict(event)), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@events_bp.route("/events/bulk", methods=["POST"])
def bulk_load_events():
    data = None
    if request.is_json:
        data = request.get_json()
    if not data:
        data = request.get_json(force=True, silent=True)
    if not data:
        data = request.form.to_dict()

    if not data or "file" not in data:
        return jsonify({"error": "Missing file field"}), 400

    try:
        with open(f"data/{data['file']}", newline="") as f:
            rows = list(csv.DictReader(f))

        from peewee import chunked
        with db.atomic():
            for batch in chunked(rows, 100):
                Event.insert_many(batch).on_conflict_ignore().execute()

        db.execute_sql("SELECT setval(pg_get_serial_sequence('event', 'id'), (SELECT MAX(id) FROM event));")

        return jsonify({
            "message": f"Loaded {len(rows)} events",
            "row_count": len(rows)
        }), 201
    except FileNotFoundError:
        return jsonify({"error": f"File not found: {data['file']}"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400
