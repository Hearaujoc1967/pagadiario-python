# config.py
import os

class Config:
    # Clave secreta para sesiones
    SECRET_KEY = 'pagadiario-python-secreto-2026'
    
    # Configuración de la base de datos MySQL
    DB_HOST = 'localhost'
    DB_PORT = 3306
    DB_USER = 'root'
    DB_PASSWORD = ''  # Sin contraseña (MySQL en Termux sin clave)
    DB_NAME = 'bd_prestamo'
    
    # Configuración de sesiones
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_FILE_DIR = os.path.join(os.path.dirname(__file__), 'flask_session')
    SESSION_COOKIE_NAME = 'pagadiario_session'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Ruta base para URLs
    BASE_URL = 'http://192.168.1.38:5000'