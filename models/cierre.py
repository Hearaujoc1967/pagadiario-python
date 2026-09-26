# models/cierre.py
from database import query


class CierreModel:

    @staticmethod
    def listar_todos():
        """Lista todos los cierres registrados."""
        return query("""
            SELECT * FROM t_cierre ORDER BY fecha DESC, id DESC
        """, fetchall=True)

    @staticmethod
    def obtener_por_id(id_cierre):
        """Obtiene un cierre por su ID."""
        return query("SELECT * FROM t_cierre WHERE id = %s", (id_cierre,), fetchone=True)

    @staticmethod
    def crear(datos):
        """Registra un cierre del día."""
        return query("""
            INSERT INTO t_cierre (monto, monto_recibido, total, observaciones, fecha)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            datos.get('monto', 0),
            datos.get('monto_recibido', 0),
            datos.get('total', 0),
            datos.get('observaciones', ''),
            datos.get('fecha')
        ), commit=True)

    @staticmethod
    def eliminar(id_cierre):
        """Elimina un cierre."""
        return query("DELETE FROM t_cierre WHERE id = %s", (id_cierre,), commit=True)

    @staticmethod
    def contar():
        """Cuenta el total de cierres."""
        resultado = query("SELECT COUNT(*) AS total FROM t_cierre", fetchone=True)
        return resultado['total'] if resultado else 0

    @staticmethod
    def sumar_cierres():
        """Suma el total de todos los cierres."""
        resultado = query("SELECT COALESCE(SUM(total), 0) AS total FROM t_cierre", fetchone=True)
        return float(resultado['total']) if resultado else 0

    # ============================================================
    # CÁLCULOS DEL DÍA
    # ============================================================

    @staticmethod
    def total_cobrado_dia(fecha):
        """Suma los cobros del día."""
        resultado = query("""
            SELECT COALESCE(SUM(monto), 0) AS total
            FROM t_det_prestamo
            WHERE fecha_cobro = %s
        """, (fecha,), fetchone=True)
        return float(resultado['total']) if resultado else 0

    @staticmethod
    def total_gastos_dia(fecha):
        """Suma los gastos del día."""
        resultado = query("""
            SELECT COALESCE(SUM(total), 0) AS total
            FROM t_gasto
            WHERE fecha = %s
        """, (fecha,), fetchone=True)
        return float(resultado['total']) if resultado else 0

    @staticmethod
    def total_ingresos_caja_dia(fecha):
        """Suma los ingresos de caja del día (tipo Ingreso)."""
        resultado = query("""
            SELECT COALESCE(SUM(d.monto), 0) AS total
            FROM t_det_caja d
            LEFT JOIN t_tipo_caja t ON d.id_tipo_ingreso = t.id
            WHERE d.fecha = %s AND t.descripcion LIKE 'Ingreso%%'
        """, (fecha,), fetchone=True)
        return float(resultado['total']) if resultado else 0

    @staticmethod
    def total_egresos_caja_dia(fecha):
        """Suma los egresos de caja del día (tipo Egreso)."""
        resultado = query("""
            SELECT COALESCE(SUM(d.monto), 0) AS total
            FROM t_det_caja d
            LEFT JOIN t_tipo_caja t ON d.id_tipo_ingreso = t.id
            WHERE d.fecha = %s AND t.descripcion LIKE 'Egreso%%'
        """, (fecha,), fetchone=True)
        return float(resultado['total']) if resultado else 0

    @staticmethod
    def contar_pagos_dia(fecha):
        """Cuenta cuántos pagos se hicieron en el día."""
        resultado = query("""
            SELECT COUNT(*) AS total FROM t_det_prestamo WHERE fecha_cobro = %s
        """, (fecha,), fetchone=True)
        return resultado['total'] if resultado else 0

    @staticmethod
    def contar_prestamos_dia(fecha):
        """Cuenta cuántos préstamos se otorgaron en el día."""
        resultado = query("""
            SELECT COUNT(*) AS total FROM t_prestamo WHERE fecha_prestamo = %s
        """, (fecha,), fetchone=True)
        return resultado['total'] if resultado else 0

    @staticmethod
    def contar_gastos_dia(fecha):
        """Cuenta cuántos gastos se registraron en el día."""
        resultado = query("""
            SELECT COUNT(*) AS total FROM t_gasto WHERE fecha = %s
        """, (fecha,), fetchone=True)
        return resultado['total'] if resultado else 0

    @staticmethod
    def existe_cierre(fecha):
        """Verifica si ya existe un cierre para esa fecha."""
        resultado = query("""
            SELECT COUNT(*) AS total FROM t_cierre WHERE fecha = %s
        """, (fecha,), fetchone=True)
        return resultado['total'] > 0 if resultado else False