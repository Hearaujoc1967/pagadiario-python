# database.py
import pymysql
from pymysql import Error
from config import Config

def get_connection():
    """Devuelve una conexión a la base de datos MySQL usando PyMySQL."""
    try:
        args = {
            'host': Config.DB_HOST,
            'port': Config.DB_PORT,
            'user': Config.DB_USER,
            'password': Config.DB_PASSWORD,
            'database': Config.DB_NAME,
            'charset': 'utf8mb4',
            'connect_timeout': 10,
            'cursorclass': pymysql.cursors.DictCursor
        }
        # Si DB_SSL es True, configuramos SSL sin verificar el certificado
        if Config.DB_SSL:
            args['ssl'] = {'ssl': {}}
            args['ssl_verify_cert'] = False
            args['ssl_verify_identity'] = False
        
        connection = pymysql.connect(**args)
        return connection
    except Error as e:
        print(f"Error conectando a MySQL: {e}")
        return None

def query(sql, params=None, fetchone=False, fetchall=False, commit=False):
    """Ejecuta una consulta SQL de forma segura."""
    conn = get_connection()
    if conn is None:
        return None
    
    cursor = conn.cursor()
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