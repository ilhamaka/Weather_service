from flask import Blueprint, request, jsonify, render_template
import logging

logger = logging.getLogger(__name__)
weather_bp = Blueprint("weather", __name__)

@weather_bp.route("/")
def index():
    """Page d'accueil avec l'interface de recherche"""
    return render_template("index.html")

@weather_bp.route("/weather", methods=["GET"])
def weather_info():
    try:
        ville_depart = request.args.get("depart", "").strip()
        ville_arrivee = request.args.get("arrivee", "").strip()
        
        ville_depart = ville_depart.replace('\n', '').replace('\r', '')
        ville_arrivee = ville_arrivee.replace('\n', '').replace('\r', '')
        
        if not ville_depart or not ville_arrivee:
            return jsonify({
                "success": False,
                "error": "Paramètres 'depart' et 'arrivee' requis"
            }), 400

        from app.services.weather_service import get_weather_for_cities
        data = get_weather_for_cities(ville_depart, ville_arrivee)
        
        return jsonify({
            "success": True,
            "data": data
        })
        
    except Exception as e:
        logger.error(f"Error in weather route: {e}")
        return jsonify({
            "success": False,
            "error": "Service temporairement indisponible",
            "message": str(e)
        }), 500

@weather_bp.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "weather-service"
    })