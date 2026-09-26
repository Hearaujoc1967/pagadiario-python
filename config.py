# config.py
import os

class Config:
    # Clave secreta para sesiones
    SECRET_KEY = os.environ.get('SECRET_KEY', 'pagadiario-python-secreto-2026')
    
    # Configuración de la base de datos MySQL
    # En local usa los valores por defecto; en Render los toma de las variables de entorno
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = int(os.environ.get('DB_PORT', 3306))
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_NAME = os.environ.get('DB_NAME', 'bd_prestamo')
    DB_SSL = os.environ.get('DB_SSL', 'false').lower() == 'true'
    
    # Configuración de sesiones
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_FILE_DIR = os.environ.get('SESSION_FILE_DIR', os.path.join(os.path.dirname(__file__), 'flask_session'))
    SESSION_COOKIE_NAME = 'pagadiario_session'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Ruta base para URLs
    # En Render se calcula dinámicamente, así que lo dejamos flexible
    BASE_URL = os.environ.get('BASE_URL', 'http://192.168.1.38:5000')