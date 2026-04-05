from flask import Blueprint, jsonify, request
from playhouse.shortcuts import model_to_dict
from app.models.url import Url
from app.models.events import Event

urls_bp = Blueprint("urls", __name__)


@urls_bp.route("/urls", methods=["GET"])
def list_urls():
    urls = Url.select()
    
    return jsonify([model_to_dict(u) for u in urls])


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
    
    required = ["user_id", "short_code", "original_url"]
    for field in required:
        if not data or field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    try:
        url = Url.create(
            user_id=data["user_id"],
            short_code=data["short_code"],
            original_url=data["original_url"],
            title=data.get("title"),
            is_active=data.get("is_active", True)
        )
        return jsonify(model_to_dict(url)), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@urls_bp.route("/<short_code>", methods=["GET"])
def redirect_url(short_code):
    try:
        url = Url.get(Url.short_code == short_code, Url.is_active == True)
        from flask import redirect
        return redirect(url.original_url, code=302)
    except Url.DoesNotExist:
        return jsonify({"error": "Short code not found or inactive"}), 404
