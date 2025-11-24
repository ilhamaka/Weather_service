from app.extensions import db  
from datetime import datetime

class WeatherData(db.Model):
    __tablename__ = "weather_data"

    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(100), nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))
    humidity = db.Column(db.Integer)
    wind_speed = db.Column(db.Float)
    last_update = db.Column(db.DateTime, default=datetime.utcnow)
