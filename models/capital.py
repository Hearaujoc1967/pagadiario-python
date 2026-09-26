# models/capital.py
from database import query


class CapitalModel:

    @staticmethod
    def obtener_capital():
        """Obtiene el registro único del capital total."""
        return query("SELECT * FROM t_capital LIMIT 1", fetchone=True)

    @staticmethod
    def listar_aportes():
        """Lista todos los aportes de capital con el nombre del socio."""
        return query("""
            SELECT 
                d.id,
                d.id_capital,
                d.id_socio,
                d.descripcion,
                d.capital AS monto,
                s.nombre AS socio
            FROM t_det_capital d
            LEFT JOIN t_socio s ON d.id_socio = s.id
            ORDER BY d.id DESC
        """, fetchall=True)

    @staticmethod
    def registrar_aporte(id_capital, id_socio, descripcion, monto):
        """Registra un aporte y suma al capital total."""
        # 1. Insertar el aporte
        query("""
            INSERT INTO t_det_capital (id_capital, id_socio, descripcion, capital)
            VALUES (%s, %s, %s, %s)
        """, (id_capital, id_socio, descripcion, monto), commit=True)
        
        # 2. Sumar el monto al capital total
        query("""
            UPDATE t_capital SET capital = capital + %s WHERE id = %s
        """, (monto, id_capital), commit=True)
        
        return True

    @staticmethod
    def actualizar_aporte(id_aporte, nuevo_monto, nueva_descripcion, nuevo_id_socio):
        """Actualiza un aporte y recalcula el capital total."""
        # 1. Obtener el aporte anterior
        anterior = query("""
            SELECT id_capital, capital FROM t_det_capital WHERE id = %s
        """, (id_aporte,), fetchone=True)
        
        if not anterior:
            return False
        
        id_capital = anterior['id_capital']
        monto_anterior = float(anterior['capital'] or 0)
        
        # 2. Restar el monto anterior del capital
        query("""
            UPDATE t_capital SET capital = capital - %s WHERE id = %s
        """, (monto_anterior, id_capital), commit=True)
        
        # 3. Actualizar el aporte
        query("""
            UPDATE t_det_capital SET
                capital = %s,
                descripcion = %s,
                id_socio = %s
            WHERE id = %s
        """, (nuevo_monto, nueva_descripcion, nuevo_id_socio, id_aporte), commit=True)
        
        # 4. Sumar el nuevo monto
        query("""
            UPDATE t_capital SET capital = capital + %s WHERE id = %s
        """, (nuevo_monto, id_capital), commit=True)
        
        return True

    @staticmethod
    def eliminar_aporte(id_aporte):
        """Elimina un aporte y resta del capital total."""
        # 1. Obtener el aporte
        aporte = query("""
            SELECT id_capital, capital FROM t_det_capital WHERE id = %s
        """, (id_aporte,), fetchone=True)
        
        if not aporte:
            return False
        
        id_capital = aporte['id_capital']
        monto = float(aporte['capital'] or 0)
        
        # 2. Restar del capital
        query("""
            UPDATE t_capital SET capital = capital - %s WHERE id = %s
        """, (monto, id_capital), commit=True)
        
        # 3. Eliminar el aporte
        query("DELETE FROM t_det_capital WHERE id = %s", (id_aporte,), commit=True)
        
        return True

    @staticmethod
    def obtener_aporte_por_id(id_aporte):
        """Obtiene un aporte por su ID."""
        return query("""
            SELECT 
                d.*,
                s.nombre AS socio
            FROM t_det_capital d
            LEFT JOIN t_socio s ON d.id_socio = s.id
            WHERE d.id = %s
        """, (id_aporte,), fetchone=True)

    @staticmethod
    def listar_socios():
        """Lista los socios disponibles."""
        return query("SELECT * FROM t_socio ORDER BY nombre", fetchall=True)

    @staticmethod
    def sumar_aportes():
        """Suma todos los aportes."""
        resultado = query("""
            SELECT COALESCE(SUM(capital), 0) AS total FROM t_det_capital
        """, fetchone=True)
        return float(resultado['total']) if resultado else 0

    @staticmethod
    def inicializar_capital():
        """Crea el registro de capital si no existe."""
        existente = query("SELECT id FROM t_capital LIMIT 1", fetchone=True)
        if not existente:
            query("INSERT INTO t_capital (capital) VALUES (0)", commit=True)
            return query("SELECT * FROM t_capital LIMIT 1", fetchone=True)
        return existente