# models/caja.py
from database import query


class CajaModel:

    @staticmethod
    def obtener_caja_principal():
        """Obtiene la caja de la sucursal principal."""
        return query("""
            SELECT 
                c.id AS id_caja,
                c.id_sucursal,
                c.total_caja,
                s.descripcion AS sucursal,
                s.direccion AS direccion_sucursal
            FROM t_caja c
            LEFT JOIN t_sucursal s ON c.id_sucursal = s.id
            LIMIT 1
        """, fetchone=True)

    @staticmethod
    def listar_movimientos(id_caja=None, limite=50):
        """Lista los movimientos de caja."""
        if id_caja:
            return query("""
                SELECT 
                    d.id,
                    d.id_caja,
                    d.id_tipo_ingreso,
                    d.monto,
                    d.fecha,
                    t.descripcion AS tipo_movimiento,
                    CASE 
                        WHEN t.descripcion LIKE 'Ingreso%%' THEN 'ingreso'
                        ELSE 'egreso'
                    END AS clase
                FROM t_det_caja d
                LEFT JOIN t_tipo_caja t ON d.id_tipo_ingreso = t.id
                WHERE d.id_caja = %s
                ORDER BY d.id DESC
                LIMIT %s
            """, (id_caja, limite), fetchall=True)
        else:
            return query("""
                SELECT 
                    d.id,
                    d.id_caja,
                    d.id_tipo_ingreso,
                    d.monto,
                    d.fecha,
                    t.descripcion AS tipo_movimiento,
                    CASE 
                        WHEN t.descripcion LIKE 'Ingreso%%' THEN 'ingreso'
                        ELSE 'egreso'
                    END AS clase
                FROM t_det_caja d
                LEFT JOIN t_tipo_caja t ON d.id_tipo_ingreso = t.id
                ORDER BY d.id DESC
                LIMIT %s
            """, (limite,), fetchall=True)

    @staticmethod
    def registrar_movimiento(id_caja, id_tipo_ingreso, monto, fecha):
        """Registra un movimiento de caja (ingreso o egreso) y actualiza el total."""
        query("""
            INSERT INTO t_det_caja (id_caja, id_tipo_ingreso, monto, fecha)
            VALUES (%s, %s, %s, %s)
        """, (id_caja, id_tipo_ingreso, monto, fecha), commit=True)
        
        tipo = query("SELECT descripcion FROM t_tipo_caja WHERE id = %s", 
                     (id_tipo_ingreso,), fetchone=True)
        es_ingreso = tipo and 'Ingreso' in tipo['descripcion']
        
        if es_ingreso:
            query("UPDATE t_caja SET total_caja = total_caja + %s WHERE id = %s",
                  (monto, id_caja), commit=True)
        else:
            query("UPDATE t_caja SET total_caja = total_caja - %s WHERE id = %s",
                  (monto, id_caja), commit=True)
        
        return True

    @staticmethod
    def listar_tipos_movimiento():
        """Lista los tipos de movimiento disponibles."""
        return query("SELECT * FROM t_tipo_caja ORDER BY id", fetchall=True)

    @staticmethod
    def obtener_total_general():
        """Suma el total de todas las cajas."""
        resultado = query("SELECT COALESCE(SUM(total_caja), 0) AS total FROM t_caja", fetchone=True)
        return float(resultado['total']) if resultado else 0

    @staticmethod
    def contar_movimientos():
        """Cuenta el total de movimientos."""
        resultado = query("SELECT COUNT(*) AS total FROM t_det_caja", fetchone=True)
        return resultado['total'] if resultado else 0

    @staticmethod
    def sumar_ingresos():
        """Suma todos los ingresos."""
        resultado = query("""
            SELECT COALESCE(SUM(d.monto), 0) AS total
            FROM t_det_caja d
            LEFT JOIN t_tipo_caja t ON d.id_tipo_ingreso = t.id
            WHERE t.descripcion LIKE 'Ingreso%%'
        """, fetchone=True)
        return float(resultado['total']) if resultado else 0

    @staticmethod
    def sumar_egresos():
        """Suma todos los egresos."""
        resultado = query("""
            SELECT COALESCE(SUM(d.monto), 0) AS total
            FROM t_det_caja d
            LEFT JOIN t_tipo_caja t ON d.id_tipo_ingreso = t.id
            WHERE t.descripcion LIKE 'Egreso%%'
        """, fetchone=True)
        return float(resultado['total']) if resultado else 0

    @staticmethod
    def obtener_movimiento_por_id(id_movimiento):
        """Obtiene un movimiento de caja por su ID."""
        return query("""
            SELECT 
                d.*,
                t.descripcion AS tipo_movimiento,
                CASE 
                    WHEN t.descripcion LIKE 'Ingreso%%' THEN 'ingreso'
                    ELSE 'egreso'
                END AS clase
            FROM t_det_caja d
            LEFT JOIN t_tipo_caja t ON d.id_tipo_ingreso = t.id
            WHERE d.id = %s
        """, (id_movimiento,), fetchone=True)

    @staticmethod
    def actualizar_movimiento(id_movimiento, id_caja, nuevos_datos):
        """Actualiza un movimiento y recalcula el total de la caja."""
        anterior = CajaModel.obtener_movimiento_por_id(id_movimiento)
        if not anterior:
            return False
        
        # Revertir el monto anterior
        if anterior['clase'] == 'ingreso':
            query("UPDATE t_caja SET total_caja = total_caja - %s WHERE id = %s",
                  (anterior['monto'], id_caja), commit=True)
        else:
            query("UPDATE t_caja SET total_caja = total_caja + %s WHERE id = %s",
                  (anterior['monto'], id_caja), commit=True)
        
        # Actualizar el movimiento
        query("""
            UPDATE t_det_caja SET
                id_tipo_ingreso = %s,
                monto = %s,
                fecha = %s
            WHERE id = %s
        """, (
            nuevos_datos.get('id_tipo_ingreso'),
            nuevos_datos.get('monto'),
            nuevos_datos.get('fecha'),
            id_movimiento
        ), commit=True)
        
        # Aplicar el nuevo monto
        tipo = query("SELECT descripcion FROM t_tipo_caja WHERE id = %s",
                     (nuevos_datos.get('id_tipo_ingreso'),), fetchone=True)
        es_ingreso = tipo and 'Ingreso' in tipo['descripcion']
        
        if es_ingreso:
            query("UPDATE t_caja SET total_caja = total_caja + %s WHERE id = %s",
                  (nuevos_datos.get('monto'), id_caja), commit=True)
        else:
            query("UPDATE t_caja SET total_caja = total_caja - %s WHERE id = %s",
                  (nuevos_datos.get('monto'), id_caja), commit=True)
        
        return True

    @staticmethod
    def eliminar_movimiento(id_movimiento, id_caja):
        """Elimina un movimiento y recalcula el total de la caja."""
        mov = CajaModel.obtener_movimiento_por_id(id_movimiento)
        if not mov:
            return False
        
        # Revertir el monto
        if mov['clase'] == 'ingreso':
            query("UPDATE t_caja SET total_caja = total_caja - %s WHERE id = %s",
                  (mov['monto'], id_caja), commit=True)
        else:
            query("UPDATE t_caja SET total_caja = total_caja + %s WHERE id = %s",
                  (mov['monto'], id_caja), commit=True)
        
        # Eliminar
        query("DELETE FROM t_det_caja WHERE id = %s", (id_movimiento,), commit=True)
        return True