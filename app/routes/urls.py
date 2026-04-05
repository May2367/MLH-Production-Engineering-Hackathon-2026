import random
import string
from datetime import datetime
from flask import Blueprint, jsonify, request, redirect
from playhouse.shortcuts import model_to_dict
from app.models.url import Url
from app.models.events import Event

urls_bp = Blueprint("urls", __name__)


def generate_short_code(length=6):
    chars = string.ascii_letters + string.digits
    while True:
        code = "".join(random.choices(chars, k=length))
        if not Url.select().where(Url.short_code == code).exists():
            return code


@urls_bp.route("/urls", methods=["GET"])
def list_urls():
    query = Url.select()

    user_id = request.args.get("user_id")
    if user_id:
        query = query.where(Url.user == int(user_id))

    is_active = request.args.get("is_active")
    if is_active is not None:
        query = query.where(Url.is_active == (is_active.lower() == "true"))

    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 50))
    query = query.paginate(page, per_page)

    return jsonify([model_to_dict(u) for u in query])


@urls_bp.route("/urls/<int:url_id>", methods=["GET"])
def get_url(url_id):
    try:
        url = Url.get_by_id(url_id)
        return jsonify(model_to_dict(url))
    except Url.DoesNotExist:
        return jsonify({"error": "URL not found"}), 404


@urls_bp.route("/urls", methods=["POST"])
def create_url():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    required = ["user_id", "original_url"]
    for field in required:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    try:
        short_code = data.get("short_code") or generate_short_code()
        url = Url.create(
            user_id=data["user_id"],
            short_code=short_code,
            original_url=data["original_url"],
            title=data.get("title"),
            is_active=data.get("is_active", True),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        return jsonify(model_to_dict(url)), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@urls_bp.route("/urls/<int:url_id>", methods=["PUT"])
def update_url(url_id):
    try:
        url = Url.get_by_id(url_id)
    except Url.DoesNotExist:
        return jsonify({"error": "URL not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    if "title" in data:
        url.title = data["title"]
    if "original_url" in data:
        url.original_url = data["original_url"]
    if "is_active" in data:
        url.is_active = data["is_active"]
    if "short_code" in data:
        url.short_code = data["short_code"]

    url.updated_at = datetime.utcnow()
    url.save()
    return jsonify(model_to_dict(url)), 200


@urls_bp.route("/urls/<int:url_id>", methods=["DELETE"])
def delete_url(url_id):
    try:
        url = Url.get_by_id(url_id)
    except Url.DoesNotExist:
        return jsonify({"error": "URL not found"}), 404

    url.delete_instance()
    return jsonify({"message": "URL deleted"}), 200


@urls_bp.route("/<short_code>", methods=["GET"])
def redirect_url(short_code):
    try:
        url = Url.get(Url.short_code == short_code, Url.is_active == True)
        return redirect(url.original_url, code=302)
    except Url.DoesNotExist:
        return jsonify({"error": "Short code not found or inactive"}), 404