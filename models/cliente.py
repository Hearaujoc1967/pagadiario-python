# models/cliente.py
from database import query

class ClienteModel:
    
    @staticmethod
    def listar_todos():
        """Devuelve todos los clientes con sus joins."""
        return query("""
            SELECT 
                t_cliente.id,
                t_cliente.dni,
                t_cliente.nombre,
                t_cliente.nombre_negocio,
                t_cliente.direccion,
                t_cliente.telf,
                t_cliente.email,
                t_tipo_estado_cliente.descripcion AS estado,
                t_reputacion.descripcion AS reputacion,
                t_cobrador.nombre AS cobrador
            FROM t_cliente
            LEFT JOIN t_tipo_estado_cliente ON t_cliente.id_tipo_estado_cliente = t_tipo_estado_cliente.id
            LEFT JOIN t_reputacion ON t_cliente.id_reputacion = t_reputacion.id
            LEFT JOIN t_cobrador ON t_cliente.id_cobrador = t_cobrador.id
            ORDER BY t_cliente.id DESC
        """, fetchall=True)
    
    @staticmethod
    def contar():
        """Cuenta el total de clientes."""
        resultado = query("SELECT COUNT(*) AS total FROM t_cliente", fetchone=True)
        return resultado['total'] if resultado else 0
    
    @staticmethod
    def obtener_por_id(id_cliente):
        """Obtiene un cliente por su ID."""
        return query("""
            SELECT 
                t_cliente.*,
                t_tipo_estado_cliente.descripcion AS estado,
                t_reputacion.descripcion AS reputacion,
                t_cobrador.nombre AS cobrador
            FROM t_cliente
            LEFT JOIN t_tipo_estado_cliente ON t_cliente.id_tipo_estado_cliente = t_tipo_estado_cliente.id
            LEFT JOIN t_reputacion ON t_cliente.id_reputacion = t_reputacion.id
            LEFT JOIN t_cobrador ON t_cliente.id_cobrador = t_cobrador.id
            WHERE t_cliente.id = %s
        """, (id_cliente,), fetchone=True)
    
    @staticmethod
    def crear(datos):
        """Crea un nuevo cliente."""
        return query("""
            INSERT INTO t_cliente 
                (id_tipo_estado_cliente, id_reputacion, id_cobrador, id_documentacion,
                 dni, nombre, nombre_negocio, direccion, direccion_cobro,
                 telf, email, referencia_1, referencia_2)
            VALUES 
                (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            datos.get('id_tipo_estado_cliente', 1),
            datos.get('id_reputacion', 1),
            datos.get('id_cobrador'),
            datos.get('id_documentacion', 1),
            datos.get('dni', ''),
            datos.get('nombre', ''),
            datos.get('nombre_negocio', ''),
            datos.get('direccion', ''),
            datos.get('direccion_cobro', ''),
            datos.get('telf', ''),
            datos.get('email', ''),
            datos.get('referencia_1', ''),
            datos.get('referencia_2', '')
        ), commit=True)
    
    @staticmethod
    def actualizar(id_cliente, datos):
        """Actualiza un cliente existente."""
        return query("""
            UPDATE t_cliente SET
                dni = %s,
                nombre = %s,
                nombre_negocio = %s,
                direccion = %s,
                direccion_cobro = %s,
                telf = %s,
                email = %s,
                referencia_1 = %s,
                referencia_2 = %s
            WHERE id = %s
        """, (
            datos.get('dni', ''),
            datos.get('nombre', ''),
            datos.get('nombre_negocio', ''),
            datos.get('direccion', ''),
            datos.get('direccion_cobro', ''),
            datos.get('telf', ''),
            datos.get('email', ''),
            datos.get('referencia_1', ''),
            datos.get('referencia_2', ''),
            id_cliente
        ), commit=True)
    
    @staticmethod
    def eliminar(id_cliente):
        """Elimina un cliente."""
        return query("DELETE FROM t_cliente WHERE id = %s", (id_cliente,), commit=True)
    
    @staticmethod
    def listar_estados():
        """Lista los estados posibles."""
        return query("SELECT * FROM t_tipo_estado_cliente", fetchall=True)
    
    @staticmethod
    def listar_reputaciones():
        """Lista las reputaciones posibles."""
        return query("SELECT * FROM t_reputacion", fetchall=True)