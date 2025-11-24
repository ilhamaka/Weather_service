import requests
from datetime import datetime, timedelta
import time
import logging

logger = logging.getLogger(__name__)

# Cache mémoire simple
_cache = {}
_CACHE_TTL = 600  # 10 minutes

def cache_get(city):
    data = _cache.get(city)
    if data and time.time() - data["time"] < _CACHE_TTL:
        return data["value"]
    return None

def cache_set(city, value):
    _cache[city] = {"value": value, "time": time.time()}

def get_weather_data(city):
    """Récupère les données météo depuis l'API OpenWeatherMap"""
    api_key = "58799277743c5472935d3ef9113d76f8"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=fr"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        return {
            'temperature': data['main']['temp'],
            'description': data['weather'][0]['description'],
            'humidity': data['main']['humidity'],
            'wind_speed': data['wind']['speed'],
            'last_update': datetime.utcnow()
        }
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed for {city}: {e}")
        return None

def is_data_fresh(weather_data, max_age_minutes=10):
    """Vérifie si les données sont encore fraîches"""
    if not weather_data or not weather_data.last_update:
        return False
    
    age = datetime.utcnow() - weather_data.last_update
    return age < timedelta(minutes=max_age_minutes)

def get_db_session_with_retry():
    """Obtient une session DB avec gestion des reconnexions"""
    from app.extensions import db
    try:
        db.session.execute('SELECT 1')
        return db.session
    except Exception as e:
        logger.warning("Database connection lost, reconnecting...")
        db.session.remove()
        time.sleep(1)
        return db.session

def save_weather_to_db(city, weather_data):
    """Sauvegarde les données météo en base avec gestion d'erreurs"""
    from app.models.weather_model import WeatherData
    
    session = get_db_session_with_retry()
    
    try:
        existing = session.query(WeatherData).filter_by(city=city).first()
        
        if existing:
            existing.temperature = weather_data['temperature']
            existing.description = weather_data['description']
            existing.humidity = weather_data['humidity']
            existing.wind_speed = weather_data['wind_speed']
            existing.last_update = weather_data['last_update']
        else:
            new_data = WeatherData(
                city=city,
                temperature=weather_data['temperature'],
                description=weather_data['description'],
                humidity=weather_data['humidity'],
                wind_speed=weather_data['wind_speed'],
                last_update=weather_data['last_update']
            )
            session.add(new_data)
        
        session.commit()
        logger.info(f"Weather data saved for {city}")
        
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to save weather data for {city}: {e}")
    finally:
        session.close()

def get_city_weather_with_cache(city):
    """Récupère les données d'une ville avec cache mémoire + cache DB"""
    
    # 1. VÉRIFIER LE CACHE MÉMOIRE EN PREMIER
    cached_memory = cache_get(city)
    if cached_memory:
        logger.info(f"Cache mémoire HIT pour {city}")
        return {**cached_memory, 'source': 'cache_memoire'}
    
    # 2. SI PAS EN CACHE MÉMOIRE, VÉRIFIER LA BASE DE DONNÉES
    from app.models.weather_model import WeatherData
    
    session = get_db_session_with_retry()
    try:
        cached_db = session.query(WeatherData).filter_by(city=city).first()
        
        if cached_db and is_data_fresh(cached_db):
            logger.info(f"Cache DB HIT pour {city}")
            # Préparer les données du cache DB
            db_data = {
                'city': cached_db.city,
                'temperature': cached_db.temperature,
                'description': cached_db.description,
                'humidity': cached_db.humidity,
                'wind_speed': cached_db.wind_speed,
                'last_update': cached_db.last_update.isoformat()
            }
            
            # STOCKER DANS LE CACHE MÉMOIRE POUR LA PROCHAINE FOIS
            cache_set(city, db_data)
            
            return {**db_data, 'source': 'cache_db'}
        
        else:
            # 3. APPEL API SI PAS DANS LES CACHES
            logger.info(f"Appel API pour {city}")
            api_data = get_weather_data(city)
            if api_data:
                # Préparer les données API
                weather_data = {
                    'city': city,
                    'temperature': api_data['temperature'],
                    'description': api_data['description'],
                    'humidity': api_data['humidity'],
                    'wind_speed': api_data['wind_speed'],
                    'last_update': api_data['last_update'].isoformat()
                }
                
                # SAUVEGARDER DANS LES DEUX CACHES
                save_weather_to_db(city, api_data)  # Cache DB
                cache_set(city, weather_data)  # Cache mémoire
                
                return {**weather_data, 'source': 'api'}
            else:
                return {'error': 'Données non disponibles', 'source': 'error'}
                
    except Exception as e:
        logger.error(f"Error processing city {city}: {e}")
        return {'error': 'Erreur lors du traitement', 'source': 'error'}
    finally:
        session.close()

def get_weather_for_cities(ville_depart, ville_arrivee):
    """Récupère les données météo pour deux villes AVEC CACHE MÉMOIRE"""
    logger.info(f"Recherche météo: {ville_depart} -> {ville_arrivee}")
    
    result = {
        'depart': get_city_weather_with_cache(ville_depart),
        'arrivee': get_city_weather_with_cache(ville_arrivee),
        'timestamp': datetime.utcnow().isoformat()
    }
    
    return result