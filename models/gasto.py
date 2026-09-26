# models/gasto.py
from database import query


class GastoModel:

    @staticmethod
    def listar_todos():
        """Lista todos los gastos con datos del cobrador."""
        return query("""
            SELECT 
                g.id,
                g.id_cobrador,
                g.total,
                g.fecha,
                c.nombre AS cobrador
            FROM t_gasto g
            LEFT JOIN t_cobrador c ON g.id_cobrador = c.id
            ORDER BY g.id DESC
        """, fetchall=True)

    @staticmethod
    def contar():
        resultado = query("SELECT COUNT(*) AS total FROM t_gasto", fetchone=True)
        return resultado['total'] if resultado else 0

    @staticmethod
    def sumar_total():
        resultado = query("SELECT COALESCE(SUM(total), 0) AS total FROM t_gasto", fetchone=True)
        return float(resultado['total']) if resultado else 0

    @staticmethod
    def obtener_por_id(id_gasto):
        """Obtiene un gasto con su detalle."""
        gasto = query("""
            SELECT 
                g.id,
                g.id_cobrador,
                g.total,
                g.fecha,
                c.nombre AS cobrador
            FROM t_gasto g
            LEFT JOIN t_cobrador c ON g.id_cobrador = c.id
            WHERE g.id = %s
        """, (id_gasto,), fetchone=True)
        
        if not gasto:
            return None
        
        detalles = query("""
            SELECT 
                d.id,
                d.id_gasto,
                d.id_tipo_gasto,
                d.descripcion,
                d.cantidad,
                d.monto,
                t.descripcion AS tipo_gasto
            FROM t_det_gasto d
            LEFT JOIN t_tipo_gasto t ON d.id_tipo_gasto = t.id
            WHERE d.id_gasto = %s
            ORDER BY d.id ASC
        """, (id_gasto,), fetchall=True)
        
        gasto['detalles'] = detalles or []
        return gasto

    @staticmethod
    def crear(id_cobrador, fecha, detalles):
        """Crea un gasto con su detalle."""
        # 1. Calcular el total
        total = sum(float(d.get('monto', 0)) for d in detalles)
        
        # 2. Insertar la cabecera
        id_gasto = query("""
            INSERT INTO t_gasto (id_cobrador, total, fecha)
            VALUES (%s, %s, %s)
        """, (id_cobrador, total, fecha), commit=True)
        
        # 3. Insertar cada detalle
        for d in detalles:
            query("""
                INSERT INTO t_det_gasto (id_gasto, id_tipo_gasto, descripcion, cantidad, monto)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                id_gasto,
                d.get('id_tipo_gasto'),
                d.get('descripcion', ''),
                d.get('cantidad', 1),
                d.get('monto', 0)
            ), commit=True)
        
        return id_gasto

    @staticmethod
    def actualizar(id_gasto, id_cobrador, fecha, detalles):
        """Actualiza un gasto y su detalle (borra y reinserta los detalles)."""
        # 1. Calcular el total
        total = sum(float(d.get('monto', 0)) for d in detalles)
        
        # 2. Actualizar la cabecera
        query("""
            UPDATE t_gasto SET id_cobrador = %s, total = %s, fecha = %s
            WHERE id = %s
        """, (id_cobrador, total, fecha, id_gasto), commit=True)
        
        # 3. Borrar todos los detalles anteriores
        query("DELETE FROM t_det_gasto WHERE id_gasto = %s", (id_gasto,), commit=True)
        
        # 4. Insertar los nuevos detalles
        for d in detalles:
            query("""
                INSERT INTO t_det_gasto (id_gasto, id_tipo_gasto, descripcion, cantidad, monto)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                id_gasto,
                d.get('id_tipo_gasto'),
                d.get('descripcion', ''),
                d.get('cantidad', 1),
                d.get('monto', 0)
            ), commit=True)
        
        return True

    @staticmethod
    def eliminar(id_gasto):
        """Elimina un gasto y su detalle (CASCADE)."""
        return query("DELETE FROM t_gasto WHERE id = %s", (id_gasto,), commit=True)

    @staticmethod
    def listar_tipos_gasto():
        """Lista los tipos de gasto disponibles."""
        return query("SELECT * FROM t_tipo_gasto ORDER BY descripcion", fetchall=True)

    @staticmethod
    def listar_cobradores():
        """Lista los cobradores disponibles."""
        return query("SELECT id, nombre FROM t_cobrador ORDER BY nombre", fetchall=True)