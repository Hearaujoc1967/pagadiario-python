# models/prestamo.py
from database import query
from datetime import date, timedelta

class PrestamoModel:
    
    @staticmethod
    def listar_todos():
        """Lista todos los préstamos con datos de cliente, cobrador y estado."""
        return query("""
            SELECT 
                p.id,
                p.fecha_prestamo,
                p.monto_prestado,
                p.monto_aprobado,
                p.interes,
                p.total_prestado,
                p.numero_cuotas,
                p.monto_x_cuotas,
                p.total_debe,
                p.cuotas_debe,
                p.fecha_prox_cobro,
                c.nombre AS cliente,
                c.dni AS cliente_dni,
                cb.nombre AS cobrador,
                e.descripcion AS estado_prestamo,
                tp.descripcion AS tipo_prestamo,
                mp.descripcion AS metodo_pago
            FROM t_prestamo p
            LEFT JOIN t_cliente c ON p.id_cliente = c.id
            LEFT JOIN t_cobrador cb ON p.id_cobrador = cb.id
            LEFT JOIN t_estado_prestamo e ON p.id_estado_prestamo = e.id
            LEFT JOIN t_tipo_prestamo tp ON p.id_tipo_prestamo = tp.id
            LEFT JOIN t_metodo_pago mp ON p.id_metodo_pago = mp.id
            ORDER BY p.id DESC
        """, fetchall=True)
    
    @staticmethod
    def listar_por_estado(id_estado):
        """Lista préstamos filtrados por estado."""
        return query("""
            SELECT 
                p.id,
                p.fecha_prestamo,
                p.monto_prestado,
                p.total_prestado,
                p.numero_cuotas,
                p.monto_x_cuotas,
                p.total_debe,
                c.nombre AS cliente,
                e.descripcion AS estado_prestamo
            FROM t_prestamo p
            LEFT JOIN t_cliente c ON p.id_cliente = c.id
            LEFT JOIN t_estado_prestamo e ON p.id_estado_prestamo = e.id
            WHERE p.id_estado_prestamo = %s
            ORDER BY p.id DESC
        """, (id_estado,), fetchall=True)
    
    @staticmethod
    def contar_por_estado(id_estado):
        """Cuenta préstamos por estado."""
        resultado = query(
            "SELECT COUNT(*) AS total FROM t_prestamo WHERE id_estado_prestamo = %s",
            (id_estado,), fetchone=True
        )
        return resultado['total'] if resultado else 0
    
    @staticmethod
    def obtener_por_id(id_prestamo):
        """Obtiene un préstamo por su ID."""
        return query("""
            SELECT 
                p.*,
                c.nombre AS cliente,
                c.dni AS cliente_dni,
                c.telf AS cliente_telf,
                cb.nombre AS cobrador,
                e.descripcion AS estado_prestamo,
                tp.descripcion AS tipo_prestamo,
                mp.descripcion AS metodo_pago
            FROM t_prestamo p
            LEFT JOIN t_cliente c ON p.id_cliente = c.id
            LEFT JOIN t_cobrador cb ON p.id_cobrador = cb.id
            LEFT JOIN t_estado_prestamo e ON p.id_estado_prestamo = e.id
            LEFT JOIN t_tipo_prestamo tp ON p.id_tipo_prestamo = tp.id
            LEFT JOIN t_metodo_pago mp ON p.id_metodo_pago = mp.id
            WHERE p.id = %s
        """, (id_prestamo,), fetchone=True)
    
    @staticmethod
    def crear(datos):
        """Crea un nuevo préstamo."""
        return query("""
            INSERT INTO t_prestamo 
                (id_estado_prestamo, id_cliente, id_cobrador, id_tipo_prestamo, 
                 id_metodo_pago, porcentaje, monto_prestado, interes, total_prestado,
                 numero_cuotas, monto_x_cuotas, total_debe, cuotas_debe, fecha_prestamo)
            VALUES 
                (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            datos.get('id_estado_prestamo', 1),
            datos.get('id_cliente'),
            datos.get('id_cobrador'),
            datos.get('id_tipo_prestamo', 1),
            datos.get('id_metodo_pago', 1),
            datos.get('porcentaje', 0),
            datos.get('monto_prestado', 0),
            datos.get('interes', 0),
            datos.get('total_prestado', 0),
            datos.get('numero_cuotas', 1),
            datos.get('monto_x_cuotas', 0),
            datos.get('total_debe', 0),
            datos.get('numero_cuotas', 1),
            datos.get('fecha_prestamo', date.today().strftime('%Y-%m-%d'))
        ), commit=True)
    
    @staticmethod
    def aprobar(id_prestamo, datos_aprobacion):
        """Aprueba un préstamo (cambia estado a 2 = Activo)."""
        return query("""
            UPDATE t_prestamo SET
                id_estado_prestamo = 2,
                monto_aprobado = %s,
                porcentaje_aprobado = %s,
                interes = %s,
                total_prestado = %s,
                total_debe = %s,
                numero_cuotas_aprobadas = %s,
                monto_x_cuotas = %s,
                cuotas_debe = %s,
                fecha_aprobacion_prestamo = %s,
                fecha_prox_cobro = %s,
                observacion = %s
            WHERE id = %s
        """, (
            datos_aprobacion.get('monto_aprobado'),
            datos_aprobacion.get('porcentaje_aprobado'),
            datos_aprobacion.get('interes'),
            datos_aprobacion.get('total_prestado'),
            datos_aprobacion.get('total_debe'),
            datos_aprobacion.get('numero_cuotas_aprobadas'),
            datos_aprobacion.get('monto_x_cuotas'),
            datos_aprobacion.get('numero_cuotas_aprobadas'),
            date.today().strftime('%Y-%m-%d'),
            datos_aprobacion.get('fecha_prox_cobro'),
            datos_aprobacion.get('observacion', ''),
            id_prestamo
        ), commit=True)
    
    @staticmethod
    def eliminar(id_prestamo):
        """Elimina un préstamo (y sus detalles por CASCADE)."""
        return query("DELETE FROM t_prestamo WHERE id = %s", (id_prestamo,), commit=True)
    
    @staticmethod
    def registrar_pago(id_prestamo, datos_pago):
        """Registra un pago en t_det_prestamo y actualiza el préstamo."""
        # 1. Insertar el pago
        query("""
            INSERT INTO t_det_prestamo 
                (id_prestamo, id_tipo_prestamo_2, cuota, descripcion, monto, fecha_cobro, fecha_prox_cobro)
            VALUES 
                (%s, %s, %s, %s, %s, %s, %s)
        """, (
            id_prestamo,
            datos_pago.get('id_tipo_prestamo_2', 2),
            datos_pago.get('cuota', 0),
            datos_pago.get('descripcion', 'Pago Efectuado'),
            datos_pago.get('monto', 0),
            datos_pago.get('fecha_cobro', date.today().strftime('%Y-%m-%d')),
            datos_pago.get('fecha_prox_cobro')
        ), commit=True)
        
        # 2. Obtener el préstamo actualizado
        prestamo = PrestamoModel.obtener_por_id(id_prestamo)
        if not prestamo:
            return False
        
        # 3. Calcular nuevos valores
        cuotas_amortizadas = (prestamo['cuotas_amortizadas'] or 0) + 1
        cuotas_debe = max(0, (prestamo['cuotas_debe'] or 0) - 1)
        total_debe = max(0, float(prestamo['total_debe'] or 0) - float(datos_pago.get('monto', 0)))
        
        # 4. Determinar el nuevo estado
        if cuotas_debe == 0:
            nuevo_estado = 3  # Finalizado
        else:
            nuevo_estado = 2  # Activo
        
        # 5. Actualizar
        return query("""
            UPDATE t_prestamo SET
                cuotas_amortizadas = %s,
                cuotas_debe = %s,
                total_debe = %s,
                id_estado_prestamo = %s,
                fecha_ultimo_cobro = %s,
                fecha_prox_cobro = %s
            WHERE id = %s
        """, (
            cuotas_amortizadas,
            cuotas_debe,
            total_debe,
            nuevo_estado,
            datos_pago.get('fecha_cobro', date.today().strftime('%Y-%m-%d')),
            datos_pago.get('fecha_prox_cobro'),
            id_prestamo
        ), commit=True)
    
    @staticmethod
    def listar_pagos(id_prestamo):
        """Lista los pagos de un préstamo."""
        return query("""
            SELECT 
                dp.id,
                dp.cuota,
                dp.descripcion,
                dp.monto,
                dp.fecha_cobro,
                tp2.descripcion AS tipo_pago
            FROM t_det_prestamo dp
            LEFT JOIN t_tipo_prestamo_2 tp2 ON dp.id_tipo_prestamo_2 = tp2.id
            WHERE dp.id_prestamo = %s
            ORDER BY dp.id DESC
        """, (id_prestamo,), fetchall=True)
    
    @staticmethod
    def listar_estados():
        """Lista los estados de préstamo."""
        return query("SELECT * FROM t_estado_prestamo", fetchall=True)
    
    @staticmethod
    def listar_tipos():
        """Lista los tipos de préstamo."""
        return query("SELECT * FROM t_tipo_prestamo", fetchall=True)
    
    @staticmethod
    def listar_metodos_pago():
        """Lista los métodos de pago."""
        return query("SELECT * FROM t_metodo_pago", fetchall=True)
    
    @staticmethod
    def sumar_prestamos_activos():
        """Suma el total prestado activo."""
        resultado = query("""
            SELECT COALESCE(SUM(total_debe), 0) AS total
            FROM t_prestamo WHERE id_estado_prestamo = 2
        """, fetchone=True)
        return float(resultado['total']) if resultado else 0