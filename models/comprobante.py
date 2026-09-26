# models/comprobante.py
"""
Módulo para leer comprobantes de pago (Nequi, Daviplata, Bancolombia, etc.)
Usa pyzbar para leer QR y pytesseract para OCR.
En entornos sin estas librerías (como Render gratis), el OCR se desactiva
automáticamente sin romper la aplicación.
"""
from PIL import Image, ImageEnhance, ImageFilter
import re
from datetime import datetime

# --- CARGA OPCIONAL DE OCR ---
try:
    import pytesseract
    PYTESSERACT_DISPONIBLE = True
except ImportError:
    PYTESSERACT_DISPONIBLE = False
    print("⚠️ pytesseract no disponible - OCR desactivado")

try:
    from pyzbar.pyzbar import decode as decode_qr
    PYZBAR_DISPONIBLE = True
except ImportError:
    PYZBAR_DISPONIBLE = False
    print("⚠️ pyzbar no disponible - solo se usará OCR")


class ComprobanteModel:

    @staticmethod
    def preprocesar_imagen(ruta_imagen):
        """Mejora la imagen para mejor OCR."""
        img = Image.open(ruta_imagen)
        img = img.convert('L')
        if img.width < 800:
            factor = 800 / img.width
            nuevo_tamano = (int(img.width * factor), int(img.height * factor))
            img = img.resize(nuevo_tamano, Image.LANCZOS)
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.5)
        img = img.filter(ImageFilter.SHARPEN)
        return img

    @staticmethod
    def leer_qr(ruta_imagen):
        """Lee el QR de la imagen del comprobante."""
        if not PYZBAR_DISPONIBLE:
            return None
        try:
            img = Image.open(ruta_imagen)
            resultados = decode_qr(img)
            if resultados:
                return resultados[0].data.decode('utf-8', errors='ignore')
            return None
        except Exception as e:
            print(f"Error leyendo QR: {e}")
            return None

    @staticmethod
    def leer_texto(ruta_imagen):
        """Extrae el texto de la imagen con OCR."""
        if not PYTESSERACT_DISPONIBLE:
            return ""
        try:
            img = ComprobanteModel.preprocesar_imagen(ruta_imagen)
            configs = [
                '--oem 3 --psm 6 -l spa',
                '--oem 3 --psm 4 -l spa',
                '--oem 3 --psm 3 -l spa',
            ]
            texto = ""
            for config in configs:
                texto = pytesseract.image_to_string(img, config=config)
                if texto.strip() and len(texto.strip()) > 20:
                    return texto
            return texto
        except Exception as e:
            print(f"Error leyendo texto: {e}")
            return ""

    @staticmethod
    def limpiar_monto(monto_str):
        """Convierte '70.000,00' a 70000.0"""
        try:
            monto_str = monto_str.replace('$', '').replace(' ', '').strip()
            if ',' in monto_str:
                monto_str = monto_str.replace('.', '').replace(',', '.')
            return float(monto_str)
        except ValueError:
            return None

    @staticmethod
    def extraer_monto(texto):
        """Extrae el monto del texto."""
        patrones = [
            r'\$\s*([\d\.]+,\d{2})',
            r'\$\s*([\d\.]+)',
            r'([\d\.]+,\d{2})',
            r'([\d\.]+)\s*pesos',
            r'Cu[aá]nto\??\s*:?\s*\$?\s*([\d\.]+)',
        ]
        for patron in patrones:
            matches = re.findall(patron, texto, re.IGNORECASE)
            for match in matches:
                monto = ComprobanteModel.limpiar_monto(match)
                if monto and monto > 0:
                    return monto
        return None

    @staticmethod
    def extraer_fecha(texto):
        """Extrae la fecha (soporta texto pegado sin espacios)."""
        meses = {
            'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
            'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
            'septiembre': 9, 'setiembre': 9, 'octubre': 10,
            'noviembre': 11, 'diciembre': 12
        }
        texto_lower = texto.lower()

        patron1 = r'(\d{1,2})\s*de\s*([a-záéíóú]+)\s*de\s*(\d{4})'
        match = re.search(patron1, texto_lower)
        if match:
            dia = int(match.group(1))
            mes_texto = match.group(2).strip()
            anio = int(match.group(3))
            mes = meses.get(mes_texto)
            if mes:
                try:
                    return datetime(anio, mes, dia).strftime('%Y-%m-%d')
                except ValueError:
                    pass

        patron2 = r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})'
        match = re.search(patron2, texto)
        if match:
            dia = int(match.group(1))
            mes = int(match.group(2))
            anio = int(match.group(3))
            if anio < 100:
                anio += 2000
            try:
                return datetime(anio, mes, dia).strftime('%Y-%m-%d')
            except ValueError:
                pass
        return None

    @staticmethod
    def extraer_hora(texto):
        """Extrae la hora corrigiendo errores comunes del OCR."""
        patrones = [
            r'(\d{1,2}):(\d{2})\s*(a\.?\s*m\.?|p\.?\s*m\.?)',
            r'(\d{1,2}):(\d{2}):(\d{2})',
            r'(\d{1,2}):(\d{2})',
        ]
        for patron in patrones:
            matches = re.findall(patron, texto, re.IGNORECASE)
            for match in matches:
                hora = int(match[0])
                minuto = int(match[1])

                if hora > 23:
                    hora_str = str(hora)
                    if len(hora_str) >= 2:
                        hora_alt = int(hora_str[1:])
                        if 0 <= hora_alt <= 23:
                            hora = hora_alt
                    if hora > 23:
                        hora = hora - 20

                if 0 <= hora <= 23 and 0 <= minuto <= 59:
                    return f"{hora:02d}:{minuto:02d}"
        return None

    @staticmethod
    def extraer_referencia(texto):
        """Extrae la referencia (soporta minúsculas del OCR)."""
        patrones = [
            r'[Rr]eferencia[:\s]*([A-Za-z0-9]{4,})',
            r'[Rr]ef[:\s]*([A-Za-z0-9]{4,})',
        ]
        for patron in patrones:
            match = re.search(patron, texto)
            if match:
                ref = match.group(1).strip().upper()
                ref = ref.replace('MI', 'M1').replace('O', '0').replace('I', '1')
                return ref
        return None

    @staticmethod
    def detectar_banco(texto):
        """Detecta el banco según palabras clave."""
        texto_lower = texto.lower()
        if 'envío exitoso' in texto_lower or 'envio exitoso' in texto_lower:
            return 'Nequi'
        if 'pago exitoso' in texto_lower:
            return 'Nequi'
        if 'nequi' in texto_lower:
            return 'Nequi'
        if 'daviplata' in texto_lower:
            return 'Daviplata'
        if 'bancolombia' in texto_lower:
            return 'Bancolombia'
        if 'davivienda' in texto_lower:
            return 'Davivienda'
        if 'bbva' in texto_lower:
            return 'BBVA'
        return 'Desconocido'

    @staticmethod
    def extraer_destinatario(texto):
        """Intenta extraer el nombre del destinatario/cliente."""
        patrones = [
            r'Para[:\s]+([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+){0,3})',
            r'Pagado en[:\s]+([A-ZÁÉÍÓÚÑ][^\n]+)',
            r'Pago en[:\s]+([A-ZÁÉÍÓÚÑ][^\n]+)',
        ]
        for patron in patrones:
            match = re.search(patron, texto)
            if match:
                nombre = match.group(1).strip()
                nombre = re.sub(r'\s+', ' ', nombre)
                for palabra in ['Fecha', 'Referencia', '¿Cuánto', 'Número', 'Conversación', '¿De dónde']:
                    if palabra in nombre:
                        nombre = nombre.split(palabra)[0].strip()
                if len(nombre) > 3:
                    return nombre
        return None

    @staticmethod
    def procesar_comprobante(ruta_imagen, tipo='envio'):
        """
        Procesa el comprobante y devuelve los datos extraídos.
        Args:
            ruta_imagen: ruta de la imagen
            tipo: 'envio' o 'pago'
        """
        resultado = {
            'monto': None,
            'fecha': None,
            'hora': None,
            'referencia': None,
            'banco': None,
            'destinatario': None,
            'qr_texto': None,
            'texto_completo': '',
            'tipo': tipo,
            'exito': False,
            'es_valido': False,
            'mensaje': ''
        }

        # Si no hay OCR disponible, devolvemos un mensaje claro
        if not PYTESSERACT_DISPONIBLE and not PYZBAR_DISPONIBLE:
            resultado['mensaje'] = 'OCR y QR no disponibles en este entorno. Verifica manualmente.'
            return resultado

        qr_data = ComprobanteModel.leer_qr(ruta_imagen)
        if qr_data:
            resultado['qr_texto'] = qr_data

        texto = ComprobanteModel.leer_texto(ruta_imagen)
        resultado['texto_completo'] = texto

        if not texto.strip():
            resultado['mensaje'] = 'No se pudo leer el texto del comprobante.'
            return resultado

        resultado['monto'] = ComprobanteModel.extraer_monto(texto)
        resultado['fecha'] = ComprobanteModel.extraer_fecha(texto)
        resultado['hora'] = ComprobanteModel.extraer_hora(texto)
        resultado['referencia'] = ComprobanteModel.extraer_referencia(texto)
        resultado['banco'] = ComprobanteModel.detectar_banco(texto)
        resultado['destinatario'] = ComprobanteModel.extraer_destinatario(texto)

        texto_lower = texto.lower()
        palabras_clave = [
            'pago exitoso', 'envío exitoso', 'envio exitoso',
            'comprobante', 'movimiento', 'nequi', 'transferencia'
        ]
        es_valido = any(p in texto_lower for p in palabras_clave) or bool(resultado['monto'])
        resultado['es_valido'] = bool(es_valido)

        if resultado['monto'] and resultado['es_valido']:
            resultado['exito'] = True
            resultado['mensaje'] = 'Comprobante procesado correctamente.'
        elif resultado['monto']:
            resultado['exito'] = True
            resultado['mensaje'] = 'Monto detectado, pero verifica que sea un comprobante válido.'
        else:
            resultado['mensaje'] = 'No se pudo detectar el monto. Verifica manualmente.'

        return resultado