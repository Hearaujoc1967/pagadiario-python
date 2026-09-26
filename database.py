# database.py
import mysql.connector
from mysql.connector import Error
from config import Config

def get_connection():
    """Devuelve una conexión a la base de datos MySQL."""
    try:
        # Argumentos base
        args = {
            'host': Config.DB_HOST,
            'port': Config.DB_PORT,
            'user': Config.DB_USER,
            'password': Config.DB_PASSWORD,
            'database': Config.DB_NAME,
            'charset': 'utf8mb4',
            'collation': 'utf8mb4_general_ci',
            'connect_timeout': 10
        }
        # Si DB_SSL es True, agregamos SSL (obligatorio en Aiven)
        if Config.DB_SSL:
            args['ssl_disabled'] = False
            args['ssl_verify_cert'] = False
        
        connection = mysql.connector.connect(**args)
        return connection
    except Error as e:
        print(f"Error conectando a MySQL: {e}")
        return None

def query(sql, params=None, fetchone=False, fetchall=False, commit=False):
    """
    Ejecuta una consulta SQL de forma segura.
    - fetchone: devuelve una sola fila como diccionario
    - fetchall: devuelve todas las filas como lista de diccionarios
    - commit: si es True, hace commit (para INSERT/UPDATE/DELETE)
    Devuelve el último ID insertado si es un INSERT.
    """
    conn = get_connection()
    if conn is None:
        return None
    
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(sql, params or ())
        
        if commit:
            conn.commit()
            last_id = cursor.lastrowid
            cursor.close()
            conn.close()
            return last_id
        
        if fetchone:
            result = cursor.fetchone()
        elif fetchall:
            result = cursor.fetchall()
        else:
            result = None
        
        cursor.close()
        conn.close()
        return result
    except Error as e:
        print(f"Error en la consulta: {e}")
        cursor.close()
        conn.close()
        return None