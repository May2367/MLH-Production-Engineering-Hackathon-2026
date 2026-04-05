from flask import Blueprint, jsonify
from playhouse.shortcuts import model_to_dict
from app.models.events import Event

events_bp = Blueprint("events", __name__)


@events_bp.route("/events", methods=["GET"])
def list_events():
    events = Event.select()
    return jsonify([model_to_dict(e) for e in events])


@events_bp.route("/events/<int:event_id>", methods=["GET"])
def get_event(event_id):
    try:
        event = Event.get_by_id(event_id)
        return jsonify(model_to_dict(event))
    except Event.DoesNotExist:
        return jsonify({"error": "Event not found"}), 404
