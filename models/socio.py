# models/socio.py
from database import query


class SocioModel:

    @staticmethod
    def listar_todos():
        """Lista todos los socios con datos del usuario."""
        return query("""
            SELECT 
                s.id,
                s.nombre,
                s.id_usuario,
                u.nombre AS usuario_nombre,
                u.login AS usuario_login
            FROM t_socio s
            LEFT JOIN t_usuario u ON s.id_usuario = u.id
            ORDER BY s.id DESC
        """, fetchall=True)

    @staticmethod
    def contar():
        """Cuenta el total de socios."""
        resultado = query("SELECT COUNT(*) AS total FROM t_socio", fetchone=True)
        return resultado['total'] if resultado else 0

    @staticmethod
    def obtener_por_id(id_socio):
        """Obtiene un socio por su ID."""
        return query("""
            SELECT s.*, u.nombre AS usuario_nombre, u.login AS usuario_login
            FROM t_socio s
            LEFT JOIN t_usuario u ON s.id_usuario = u.id
            WHERE s.id = %s
        """, (id_socio,), fetchone=True)

    @staticmethod
    def crear(datos):
        """Crea un nuevo socio."""
        return query("""
            INSERT INTO t_socio (id_usuario, nombre)
            VALUES (%s, %s)
        """, (
            datos.get('id_usuario'),
            datos.get('nombre', '')
        ), commit=True)

    @staticmethod
    def actualizar(id_socio, datos):
        """Actualiza un socio existente."""
        return query("""
            UPDATE t_socio SET
                id_usuario = %s,
                nombre = %s
            WHERE id = %s
        """, (
            datos.get('id_usuario'),
            datos.get('nombre', ''),
            id_socio
        ), commit=True)

    @staticmethod
    def eliminar(id_socio):
        """Elimina un socio."""
        return query("DELETE FROM t_socio WHERE id = %s", (id_socio,), commit=True)

    @staticmethod
    def listar_usuarios_disponibles():
        """Lista los usuarios activos para asignar como socio."""
        return query("""
            SELECT id, nombre, login
            FROM t_usuario
            WHERE id_estado_usuario = 1
            ORDER BY nombre
        """, fetchall=True)