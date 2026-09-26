# models/empresa.py
from database import query


class EmpresaModel:

    @staticmethod
    def obtener():
        """Obtiene el registro único de la empresa."""
        return query("SELECT * FROM t_empresa LIMIT 1", fetchone=True)

    @staticmethod
    def crear(datos):
        """Crea el registro inicial de la empresa."""
        return query("""
            INSERT INTO t_empresa (nombre, nit, direccion, telefono, email, logo)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            datos.get('nombre', ''),
            datos.get('nit', ''),
            datos.get('direccion', ''),
            datos.get('telefono', ''),
            datos.get('email', ''),
            datos.get('logo', '')
        ), commit=True)

    @staticmethod
    def actualizar(id_empresa, datos):
        """Actualiza los datos de la empresa."""
        return query("""
            UPDATE t_empresa SET
                nombre = %s,
                nit = %s,
                direccion = %s,
                telefono = %s,
                email = %s,
                logo = %s
            WHERE id = %s
        """, (
            datos.get('nombre', ''),
            datos.get('nit', ''),
            datos.get('direccion', ''),
            datos.get('telefono', ''),
            datos.get('email', ''),
            datos.get('logo', ''),
            id_empresa
        ), commit=True)

    @staticmethod
    def inicializar():
        """Crea el registro si no existe."""
        existente = query("SELECT id FROM t_empresa LIMIT 1", fetchone=True)
        if not existente:
            EmpresaModel.crear({
                'nombre': 'Mi Empresa',
                'nit': '',
                'direccion': '',
                'telefono': '',
                'email': '',
                'logo': ''
            })
        return EmpresaModel.obtener()