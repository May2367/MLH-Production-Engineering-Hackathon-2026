from flask import Blueprint, jsonify
from playhouse.shortcuts import model_to_dict
from app.models.user import User

users_bp = Blueprint("users", __name__)


@users_bp.route("/users", methods=["GET"])
def list_users():
    users = User.select()
    return jsonify([model_to_dict(u) for u in users])


@users_bp.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    try:
        user = User.get_by_id(user_id)
        return jsonify(model_to_dict(user))
    except User.DoesNotExist:
        return jsonify({"error": "User not found"}), 404

def register_routes(app):
    from app.routes.urls import urls_bp
    from app.routes.users import users_bp
    from app.routes.events import events_bp

    app.register_blueprint(urls_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(events_bp)