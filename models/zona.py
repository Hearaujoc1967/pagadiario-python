# models/zona.py
from database import query


class ZonaModel:

    @staticmethod
    def listar_todas():
        """Lista todas las zonas con su asignación a cobrador."""
        return query("""
            SELECT 
                z.id,
                z.zona,
                z.direccion,
                COUNT(zc.id) AS num_cobradores
            FROM t_zona z
            LEFT JOIN t_zona_cobrador zc ON z.id = zc.id_zona
            GROUP BY z.id, z.zona, z.direccion
            ORDER BY z.id DESC
        """, fetchall=True)

    @staticmethod
    def contar():
        """Cuenta el total de zonas."""
        resultado = query("SELECT COUNT(*) AS total FROM t_zona", fetchone=True)
        return resultado['total'] if resultado else 0

    @staticmethod
    def obtener_por_id(id_zona):
        """Obtiene una zona por su ID."""
        return query("SELECT * FROM t_zona WHERE id = %s", (id_zona,), fetchone=True)

    @staticmethod
    def crear(datos):
        """Crea una nueva zona."""
        return query("""
            INSERT INTO t_zona (zona, direccion)
            VALUES (%s, %s)
        """, (
            datos.get('zona', ''),
            datos.get('direccion', '')
        ), commit=True)

    @staticmethod
    def actualizar(id_zona, datos):
        """Actualiza una zona existente."""
        return query("""
            UPDATE t_zona SET
                zona = %s,
                direccion = %s
            WHERE id = %s
        """, (
            datos.get('zona', ''),
            datos.get('direccion', ''),
            id_zona
        ), commit=True)

    @staticmethod
    def eliminar(id_zona):
        """Elimina una zona y sus asignaciones."""
        query("DELETE FROM t_zona_cobrador WHERE id_zona = %s", (id_zona,), commit=True)
        return query("DELETE FROM t_zona WHERE id = %s", (id_zona,), commit=True)


class ZonaCobradorModel:

    @staticmethod
    def listar_todas():
        """Lista todas las asignaciones zona-cobrador."""
        return query("""
            SELECT 
                zc.id,
                zc.id_zona,
                zc.id_cobrador,
                zc.id_sucursal,
                z.zona AS zona_nombre,
                z.direccion AS zona_direccion,
                c.nombre AS cobrador_nombre,
                s.descripcion AS sucursal_nombre,
                s.direccion AS sucursal_direccion
            FROM t_zona_cobrador zc
            LEFT JOIN t_zona z ON zc.id_zona = z.id
            LEFT JOIN t_cobrador c ON zc.id_cobrador = c.id
            LEFT JOIN t_sucursal s ON zc.id_sucursal = s.id
            ORDER BY zc.id DESC
        """, fetchall=True)

    @staticmethod
    def obtener_por_id(id_asignacion):
        """Obtiene una asignación por su ID."""
        return query("""
            SELECT 
                zc.*,
                z.zona AS zona_nombre,
                c.nombre AS cobrador_nombre,
                s.descripcion AS sucursal_nombre
            FROM t_zona_cobrador zc
            LEFT JOIN t_zona z ON zc.id_zona = z.id
            LEFT JOIN t_cobrador c ON zc.id_cobrador = c.id
            LEFT JOIN t_sucursal s ON zc.id_sucursal = s.id
            WHERE zc.id = %s
        """, (id_asignacion,), fetchone=True)

    @staticmethod
    def crear(datos):
        """Crea una nueva asignación."""
        return query("""
            INSERT INTO t_zona_cobrador (id_zona, id_cobrador, id_sucursal)
            VALUES (%s, %s, %s)
        """, (
            datos.get('id_zona'),
            datos.get('id_cobrador'),
            datos.get('id_sucursal')
        ), commit=True)

    @staticmethod
    def actualizar(id_asignacion, datos):
        """Actualiza una asignación existente."""
        return query("""
            UPDATE t_zona_cobrador SET
                id_zona = %s,
                id_cobrador = %s,
                id_sucursal = %s
            WHERE id = %s
        """, (
            datos.get('id_zona'),
            datos.get('id_cobrador'),
            datos.get('id_sucursal'),
            id_asignacion
        ), commit=True)

    @staticmethod
    def eliminar(id_asignacion):
        """Elimina una asignación."""
        return query("DELETE FROM t_zona_cobrador WHERE id = %s", (id_asignacion,), commit=True)

    @staticmethod
    def contar():
        """Cuenta el total de asignaciones."""
        resultado = query("SELECT COUNT(*) AS total FROM t_zona_cobrador", fetchone=True)
        return resultado['total'] if resultado else 0