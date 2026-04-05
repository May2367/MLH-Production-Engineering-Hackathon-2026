import json
from datetime import datetime
from flask import Blueprint, jsonify, request
from playhouse.shortcuts import model_to_dict
from app.models.events import Event

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