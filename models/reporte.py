# models/reporte.py
from database import query


class ReporteModel:

    @staticmethod
    def prestamos_por_fecha(fecha_i, fecha_f):
        """Lista préstamos creados entre dos fechas."""
        return query("""
            SELECT 
                p.id,
                p.fecha_prestamo,
                p.monto_prestado,
                p.interes,
                p.total_prestado,
                p.total_debe,
                p.numero_cuotas,
                p.cuotas_debe,
                c.nombre AS cliente,
                c.dni AS cliente_dni,
                cb.nombre AS cobrador,
                e.descripcion AS estado
            FROM t_prestamo p
            LEFT JOIN t_cliente c ON p.id_cliente = c.id
            LEFT JOIN t_cobrador cb ON p.id_cobrador = cb.id
            LEFT JOIN t_estado_prestamo e ON p.id_estado_prestamo = e.id
            WHERE p.fecha_prestamo >= %s AND p.fecha_prestamo <= %s
            ORDER BY p.fecha_prestamo DESC, p.id DESC
        """, (fecha_i, fecha_f), fetchall=True)

    @staticmethod
    def cobros_por_fecha(fecha_i, fecha_f):
        """Lista pagos (abonos) recibidos entre dos fechas."""
        return query("""
            SELECT 
                dp.id,
                dp.fecha_cobro,
                dp.monto,
                dp.cuota,
                dp.descripcion,
                p.id AS id_prestamo,
                c.nombre AS cliente,
                c.dni AS cliente_dni,
                cb.nombre AS cobrador,
                tp2.descripcion AS tipo_pago
            FROM t_det_prestamo dp
            LEFT JOIN t_prestamo p ON dp.id_prestamo = p.id
            LEFT JOIN t_cliente c ON p.id_cliente = c.id
            LEFT JOIN t_cobrador cb ON p.id_cobrador = cb.id
            LEFT JOIN t_tipo_prestamo_2 tp2 ON dp.id_tipo_prestamo_2 = tp2.id
            WHERE dp.fecha_cobro >= %s AND dp.fecha_cobro <= %s
            ORDER BY dp.fecha_cobro DESC, dp.id DESC
        """, (fecha_i, fecha_f), fetchall=True)

    @staticmethod
    def gastos_por_fecha(fecha_i, fecha_f):
        """Lista gastos entre dos fechas."""
        return query("""
            SELECT 
                g.id,
                g.fecha,
                g.total,
                c.nombre AS cobrador,
                (SELECT COUNT(*) FROM t_det_gasto WHERE id_gasto = g.id) AS num_items
            FROM t_gasto g
            LEFT JOIN t_cobrador c ON g.id_cobrador = c.id
            WHERE g.fecha >= %s AND g.fecha <= %s
            ORDER BY g.fecha DESC, g.id DESC
        """, (fecha_i, fecha_f), fetchall=True)

    @staticmethod
    def resumen_prestamos(fecha_i, fecha_f):
        """Resumen totalizado de préstamos en un rango."""
        return query("""
            SELECT 
                COUNT(*) AS total_prestamos,
                COALESCE(SUM(monto_prestado), 0) AS total_monto,
                COALESCE(SUM(interes), 0) AS total_interes,
                COALESCE(SUM(total_prestado), 0) AS total_a_pagar,
                COALESCE(SUM(total_debe), 0) AS total_por_cobrar
            FROM t_prestamo
            WHERE fecha_prestamo >= %s AND fecha_prestamo <= %s
        """, (fecha_i, fecha_f), fetchone=True)

    @staticmethod
    def resumen_cobros(fecha_i, fecha_f):
        """Resumen totalizado de cobros en un rango."""
        return query("""
            SELECT 
                COUNT(*) AS total_pagos,
                COALESCE(SUM(monto), 0) AS total_cobrado
            FROM t_det_prestamo
            WHERE fecha_cobro >= %s AND fecha_cobro <= %s
        """, (fecha_i, fecha_f), fetchone=True)

    @staticmethod
    def resumen_gastos(fecha_i, fecha_f):
        """Resumen totalizado de gastos en un rango."""
        return query("""
            SELECT 
                COUNT(*) AS total_gastos,
                COALESCE(SUM(total), 0) AS total_monto
            FROM t_gasto
            WHERE fecha >= %s AND fecha <= %s
        """, (fecha_i, fecha_f), fetchone=True)

    @staticmethod
    def prestamos_por_cobrador(fecha_i, fecha_f):
        """Agrupa préstamos por cobrador en un rango."""
        return query("""
            SELECT 
                COALESCE(cb.nombre, 'Sin asignar') AS cobrador,
                COUNT(p.id) AS total_prestamos,
                COALESCE(SUM(p.monto_prestado), 0) AS total_monto,
                COALESCE(SUM(p.total_debe), 0) AS total_debe
            FROM t_prestamo p
            LEFT JOIN t_cobrador cb ON p.id_cobrador = cb.id
            WHERE p.fecha_prestamo >= %s AND p.fecha_prestamo <= %s
            GROUP BY cb.nombre
            ORDER BY total_prestamos DESC
        """, (fecha_i, fecha_f), fetchall=True)

    @staticmethod
    def cobros_por_cobrador(fecha_i, fecha_f):
        """Agrupa cobros por cobrador en un rango."""
        return query("""
            SELECT 
                COALESCE(cb.nombre, 'Sin asignar') AS cobrador,
                COUNT(dp.id) AS total_pagos,
                COALESCE(SUM(dp.monto), 0) AS total_cobrado
            FROM t_det_prestamo dp
            LEFT JOIN t_prestamo p ON dp.id_prestamo = p.id
            LEFT JOIN t_cobrador cb ON p.id_cobrador = cb.id
            WHERE dp.fecha_cobro >= %s AND dp.fecha_cobro <= %s
            GROUP BY cb.nombre
            ORDER BY total_cobrado DESC
        """, (fecha_i, fecha_f), fetchall=True)

    @staticmethod
    def cobros_por_dia(fecha_i, fecha_f):
        """Agrupa cobros por día."""
        return query("""
            SELECT 
                fecha_cobro AS fecha,
                COUNT(*) AS total_pagos,
                COALESCE(SUM(monto), 0) AS total_cobrado
            FROM t_det_prestamo
            WHERE fecha_cobro >= %s AND fecha_cobro <= %s
            GROUP BY fecha_cobro
            ORDER BY fecha_cobro DESC
        """, (fecha_i, fecha_f), fetchall=True)