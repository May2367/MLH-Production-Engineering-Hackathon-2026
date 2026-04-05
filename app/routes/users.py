from flask import Blueprint, jsonify, request
from playhouse.shortcuts import model_to_dict
from app.models.user import User
from app.database import db
import csv
import io

users_bp = Blueprint("users", __name__)


@users_bp.route("/users", methods=["GET"])
def list_users():
    query = User.select()
    
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 50))
    query = query.paginate(page, per_page)

    return jsonify([model_to_dict(u) for u in query])


@users_bp.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    try:
        user = User.get_by_id(user_id)
        return jsonify(model_to_dict(user))
    except User.DoesNotExist:
        return jsonify({"error": "User not found"}), 404


@users_bp.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    required = ["username", "email"]
    for field in required:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    try:
        from datetime import datetime
        user = User.create(
            username=data["username"],
            email=data["email"],
            created_at=data.get("created_at", datetime.utcnow())
        )
        return jsonify(model_to_dict(user)), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@users_bp.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    try:
        user = User.get_by_id(user_id)
    except User.DoesNotExist:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    if "username" in data:
        user.username = data["username"]
    if "email" in data:
        user.email = data["email"]

    user.save()
    return jsonify(model_to_dict(user)), 200


@users_bp.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    try:
        user = User.get_by_id(user_id)
    except User.DoesNotExist:
        return jsonify({"error": "User not found"}), 404

    user.delete_instance()
    return jsonify({"message": "User deleted"}), 200


@users_bp.route("/users/bulk", methods=["POST"])
def bulk_load_users():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict() or request.get_json(force=True, silent=True)

    if not data or "file" not in data:
        return jsonify({"error": "Missing file field"}), 400

    try:
        with open(f"data/{data['file']}", newline="") as f:
            rows = list(csv.DictReader(f))

        from peewee import chunked
        with db.atomic():
            for batch in chunked(rows, 100):
                User.insert_many(batch).on_conflict_ignore().execute()

        return jsonify({
            "message": f"Loaded {len(rows)} users",
            "row_count": len(rows)
        }), 201
    except FileNotFoundError:
        return jsonify({"error": f"File not found: {data['file']}"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400