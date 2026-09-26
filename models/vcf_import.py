# models/vcf_import.py
"""
Módulo para importar contactos desde archivos .vcf (vCard 2.1 y 3.0)
"""
import re
from datetime import datetime


class VCFImportModel:

    @staticmethod
    def decodificar_quoted_printable(texto):
        """Decodifica texto en formato QUOTED-PRINTABLE (ej: =4F=6D=61=72)."""
        try:
            # Convertir =XX a bytes y decodificar
            bytes_texto = bytes.fromhex(
                re.sub(r'=([0-9A-F]{2})', r'\1', texto)
            )
            return bytes_texto.decode('utf-8', errors='ignore')
        except Exception:
            return texto

    @staticmethod
    def parsear_vcf(contenido):
        """Parsea el contenido de un archivo VCF y devuelve lista de contactos."""
        contactos = []
        tarjetas = re.findall(
            r'BEGIN:VCARD(.*?)END:VCARD',
            contenido,
            re.DOTALL | re.IGNORECASE
        )

        for tarjeta in tarjetas:
            contacto = {
                'nombre': '',
                'nombre_completo': '',
                'telefono': '',
                'email': '',
                'direccion': '',
                'notas': ''
            }

            # Procesar cada línea
            lineas = tarjeta.strip().split('\n')
            for linea in lineas:
                linea = linea.strip()
                if not linea:
                    continue

                # Nombre completo (FN)
                if linea.startswith('FN'):
                    valor = linea.split(':', 1)[1] if ':' in linea else ''
                    if 'QUOTED-PRINTABLE' in linea:
                        valor = VCFImportModel.decodificar_quoted_printable(valor)
                    contacto['nombre_completo'] = valor.strip()

                # Nombre estructurado (N)
                elif linea.startswith('N') and not linea.startswith('NOTE'):
                    valor = linea.split(':', 1)[1] if ':' in linea else ''
                    if 'QUOTED-PRINTABLE' in linea:
                        valor = VCFImportModel.decodificar_quoted_printable(valor)
                    partes = valor.split(';')
                    if len(partes) >= 2:
                        apellido = partes[0].strip() if partes[0] else ''
                        nombre = partes[1].strip() if partes[1] else ''
                        if nombre and apellido:
                            contacto['nombre'] = f"{nombre} {apellido}".strip()
                        elif nombre:
                            contacto['nombre'] = nombre
                        elif apellido:
                            contacto['nombre'] = apellido

                # Teléfono
                elif linea.startswith('TEL'):
                    valor = linea.split(':', 1)[1] if ':' in linea else ''
                    # Limpiar el teléfono
                    tel = re.sub(r'[^\d+]', '', valor)
                    if tel and not contacto['telefono']:
                        contacto['telefono'] = tel

                # Email
                elif linea.startswith('EMAIL'):
                    valor = linea.split(':', 1)[1] if ':' in linea else ''
                    if valor and not contacto['email']:
                        contacto['email'] = valor.strip()

                # Dirección
                elif linea.startswith('ADR'):
                    valor = linea.split(':', 1)[1] if ':' in linea else ''
                    # Limpiar dirección
                    adr = valor.replace(';', ', ').strip(', ').strip()
                    if adr and not contacto['direccion']:
                        contacto['direccion'] = adr

                # Notas
                elif linea.startswith('NOTE'):
                    valor = linea.split(':', 1)[1] if ':' in linea else ''
                    contacto['notas'] = valor.strip()

            # Si no hay nombre pero hay nombre_completo, usar el FN
            if not contacto['nombre'] and contacto['nombre_completo']:
                contacto['nombre'] = contacto['nombre_completo']

            # Solo agregar si tiene al menos nombre o teléfono
            if contacto['nombre'] or contacto['telefono']:
                contactos.append(contacto)

        return contactos

    @staticmethod
    def leer_archivo_vcf(ruta):
        """Lee un archivo VCF y devuelve la lista de contactos."""
        try:
            with open(ruta, 'r', encoding='utf-8', errors='ignore') as f:
                contenido = f.read()
            return VCFImportModel.parsear_vcf(contenido)
        except Exception as e:
            print(f"Error leyendo VCF: {e}")
            return []

    @staticmethod
    def estadisticas(contactos):
        """Devuelve estadísticas de los contactos parseados."""
        return {
            'total': len(contactos),
            'con_telefono': sum(1 for c in contactos if c['telefono']),
            'con_email': sum(1 for c in contactos if c['email']),
            'con_direccion': sum(1 for c in contactos if c['direccion']),
        }