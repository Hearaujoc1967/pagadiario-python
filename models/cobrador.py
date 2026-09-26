# models/cobrador.py
from database import query


class CobradorModel:

    @staticmethod
    def listar_todos():
        """Lista todos los cobradores."""
        return query("""
            SELECT 
                c.id,
                c.nombre,
                c.id_usuario,
                u.nombre AS usuario_nombre,
                u.login AS usuario_login
            FROM t_cobrador c
            LEFT JOIN t_usuario u ON c.id_usuario = u.id
            ORDER BY c.id DESC
        """, fetchall=True)

    @staticmethod
    def contar():
        """Cuenta el total de cobradores."""
        resultado = query("SELECT COUNT(*) AS total FROM t_cobrador", fetchone=True)
        return resultado['total'] if resultado else 0

    @staticmethod
    def obtener_por_id(id_cobrador):
        """Obtiene un cobrador por su ID."""
        return query("""
            SELECT c.*, u.nombre AS usuario_nombre, u.login AS usuario_login
            FROM t_cobrador c
            LEFT JOIN t_usuario u ON c.id_usuario = u.id
            WHERE c.id = %s
        """, (id_cobrador,), fetchone=True)

    @staticmethod
    def crear(datos):
        """Crea un nuevo cobrador."""
        return query("""
            INSERT INTO t_cobrador (id_usuario, nombre)
            VALUES (%s, %s)
        """, (
            datos.get('id_usuario'),
            datos.get('nombre', '')
        ), commit=True)

    @staticmethod
    def actualizar(id_cobrador, datos):
        """Actualiza un cobrador existente."""
        return query("""
            UPDATE t_cobrador SET
                id_usuario = %s,
                nombre = %s
            WHERE id = %s
        """, (
            datos.get('id_usuario'),
            datos.get('nombre', ''),
            id_cobrador
        ), commit=True)

    @staticmethod
    def eliminar(id_cobrador):
        """Elimina un cobrador."""
        return query("DELETE FROM t_cobrador WHERE id = %s", (id_cobrador,), commit=True)

    @staticmethod
    def listar_usuarios_disponibles():
        """Lista los usuarios activos para asignar como cobrador."""
        return query("""
            SELECT id, nombre, login
            FROM t_usuario
            WHERE id_estado_usuario = 1
            ORDER BY nombre
        """, fetchall=True)