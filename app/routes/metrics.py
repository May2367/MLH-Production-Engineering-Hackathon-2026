import psutil
from flask import Blueprint, jsonify

metrics_bp = Blueprint("metrics", __name__)


@metrics_bp.route("/metrics", methods=["GET"])
def metrics():

    cpu = psutil.cpu_percent(interval=1)

    mem = psutil.virtual_memory()

    disk = psutil.disk_usage('/')

    return jsonify({
        "cpu": {
            "percent_used": cpu
        },
        "memory": {
            "total_mb": round(mem.total / 1024 / 1024, 2),
            "used_mb": round(mem.used / 1024 / 1024, 2),
            "available_mb": round(mem.available / 1024 / 1024, 2),
            "percent_used": mem.percent
        },
        "disk": {
            "total_gb": round(disk.total / 1024 / 1024 / 1024, 2),
            "used_gb": round(disk.used / 1024 / 1024 / 1024, 2),
            "free_gb": round(disk.free / 1024 / 1024 / 1024, 2),
            "percent_used": disk.percent
        }
    })