import os

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "your-api-key-here")

DB_HOST = os.getenv("DB_HOST", "Your-DB-Host-Here")
DB_PORT = os.getenv("DB_PORT", "your-db-port-here")
DB_USER = os.getenv("DB_USER", "your-db-user-here")
DB_PASSWORD = os.getenv("DB_PASSWORD", "your-db-password-here")
DB_NAME = os.getenv("DB_NAME", "your-db-name-here")

SQLALCHEMY_DATABASE_URI = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
SQLALCHEMY_TRACK_MODIFICATIONS = False
