import pymysql

try:
    conexion = pymysql.connect(
        host='127.0.0.1',
        user='root',
        password='',
        database='bd_prestamo',
        port=3306
    )
    print("✅ ¡Conexión exitosa a MariaDB desde Pydroid 3!")
    
    cursor = conexion.cursor()
    cursor.execute("SHOW TABLES;")
    tablas = cursor.fetchall()
    print(f"📋 Tablas en bd_prestamo: {tablas}")
    
    conexion.close()
except Exception as e:
    print(f"❌ Error de conexión: {e}")