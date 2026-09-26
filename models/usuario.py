# models/usuario.py
from database import query


class UsuarioModel:

    @staticmethod
    def listar_todos():
        """Lista todos los usuarios con su nivel y estado."""
        return query("""
            SELECT 
                u.id,
                u.nombre,
                u.login,
                u.clave,
                u.id_nivel,
                u.id_estado_usuario,
                n.descripcion AS nivel,
                e.descripcion AS estado
            FROM t_usuario u
            LEFT JOIN t_nivel n ON u.id_nivel = n.id
            LEFT JOIN t_estado_usuario e ON u.id_estado_usuario = e.id
            ORDER BY u.id DESC
        """, fetchall=True)

    @staticmethod
    def contar():
        """Cuenta el total de usuarios."""
        resultado = query("SELECT COUNT(*) AS total FROM t_usuario", fetchone=True)
        return resultado['total'] if resultado else 0

    @staticmethod
    def obtener_por_id(id_usuario):
        """Obtiene un usuario por su ID."""
        return query("""
            SELECT 
                u.*,
                n.descripcion AS nivel,
                e.descripcion AS estado
            FROM t_usuario u
            LEFT JOIN t_nivel n ON u.id_nivel = n.id
            LEFT JOIN t_estado_usuario e ON u.id_estado_usuario = e.id
            WHERE u.id = %s
        """, (id_usuario,), fetchone=True)

    @staticmethod
    def obtener_por_login(login):
        """Obtiene un usuario por su login."""
        return query("""
            SELECT * FROM t_usuario WHERE login = %s
        """, (login,), fetchone=True)

    @staticmethod
    def crear(datos):
        """Crea un nuevo usuario."""
        return query("""
            INSERT INTO t_usuario (id_estado_usuario, id_nivel, nombre, login, clave)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            datos.get('id_estado_usuario', 1),
            datos.get('id_nivel', 1),
            datos.get('nombre', ''),
            datos.get('login', ''),
            datos.get('clave', '')
        ), commit=True)

    @staticmethod
    def actualizar(id_usuario, datos):
        """Actualiza un usuario existente."""
        return query("""
            UPDATE t_usuario SET
                id_estado_usuario = %s,
                id_nivel = %s,
                nombre = %s,
                login = %s,
                clave = %s
            WHERE id = %s
        """, (
            datos.get('id_estado_usuario', 1),
            datos.get('id_nivel', 1),
            datos.get('nombre', ''),
            datos.get('login', ''),
            datos.get('clave', ''),
            id_usuario
        ), commit=True)

    @staticmethod
    def eliminar(id_usuario):
        """Elimina un usuario."""
        return query("DELETE FROM t_usuario WHERE id = %s", (id_usuario,), commit=True)

    @staticmethod
    def listar_niveles():
        """Lista los niveles disponibles."""
        return query("SELECT * FROM t_nivel ORDER BY id", fetchall=True)

    @staticmethod
    def listar_estados():
        """Lista los estados de usuario."""
        return query("SELECT * FROM t_estado_usuario ORDER BY id", fetchall=True)

    @staticmethod
    def verificar_login(login, clave_hash):
        """Verifica credenciales (login + hash SHA1)."""
        return query("""
            SELECT * FROM t_usuario 
            WHERE login = %s AND clave = %s
        """, (login, clave_hash), fetchone=True)

    @staticmethod
    def existe_login(login, excluir_id=None):
        """Verifica si un login ya existe (útil para validar al crear/editar)."""
        if excluir_id:
            resultado = query("""
                SELECT COUNT(*) AS total FROM t_usuario 
                WHERE login = %s AND id != %s
            """, (login, excluir_id), fetchone=True)
        else:
            resultado = query("""
                SELECT COUNT(*) AS total FROM t_usuario 
                WHERE login = %s
            """, (login,), fetchone=True)
        return resultado['total'] > 0 if resultado else False