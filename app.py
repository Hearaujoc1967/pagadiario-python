# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_session import Session
from config import Config
from database import query
import hashlib
import os
import socket
import threading
import webbrowser
from datetime import date, timedelta

app = Flask(__name__)
app.config.from_object(Config)

# Inicializar Flask-Session
Session(app)

# Crear carpeta de sesiones si no existe
os.makedirs(Config.SESSION_FILE_DIR, exist_ok=True)


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================
def sha1_hash(texto):
    """Genera el hash SHA1, igual que la función do_hash() de CodeIgniter."""
    return hashlib.sha1(texto.encode('utf-8')).hexdigest()


def obtener_ip_local():
    """Obtiene la IP local del dispositivo en la red WiFi."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def abrir_navegador(ip):
    """Abre el navegador con la URL del servidor."""
    url = f"http://{ip}:5000"
    print(f"\n>>> Abriendo navegador en: {url}\n")
    webbrowser.open(url)


# ============================================================
# RUTAS
# ============================================================
@app.route('/')
def index():
    """Página principal: redirige al login o al dashboard según la sesión."""
    if session.get('logueado'):
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Formulario de login y validación."""
    if request.method == 'POST':
        usuario = request.form.get('txt_nombre_ususario', '').strip()
        password = request.form.get('txt_pass', '').strip()
        hash_pass = sha1_hash(password)
        
        # Buscar usuario en la BD
        user = query(
            "SELECT * FROM t_usuario WHERE login = %s AND clave = %s",
            (usuario, hash_pass),
            fetchone=True
        )
        
        if user:
            # Guardar datos en sesión
            session['logueado'] = True
            session['id'] = user['id']
            session['id_estado_usuario'] = user['id_estado_usuario']
            session['id_nivel'] = user['id_nivel']
            session['nombre'] = user['nombre']
            
            if user['id_estado_usuario'] == 1:
                return redirect(url_for('dashboard'))
            else:
                flash('Usuario Inactivo', 'danger')
                return redirect(url_for('login'))
        else:
            flash('Usuario o Clave Invalidos', 'danger')
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    """Panel principal con tema oscuro estilo Premium."""
    if not session.get('logueado'):
        flash('Debe Iniciar Sesion', 'warning')
        return redirect(url_for('login'))
    
    from datetime import date
    hoy = date.today()
    hoy_str = hoy.strftime('%Y-%m-%d')
    
    # --- Filtros de fecha ---
    mes_ini = int(request.args.get('mes_ini', hoy.month))
    anio_ini = int(request.args.get('anio_ini', hoy.year))
    mes_fin = int(request.args.get('mes_fin', hoy.month))
    anio_fin = int(request.args.get('anio_fin', hoy.year))
    
    # --- KPIs ---
    from models.cliente import ClienteModel
    total_clientes = ClienteModel.contar()
    
    from models.caja import CajaModel
    caja_principal = CajaModel.obtener_caja_principal()
    total_caja = float(caja_principal['total_caja']) if caja_principal else 0
    
    # Cobrado del mes actual
    resultado = query("""
        SELECT COALESCE(SUM(monto), 0) AS total
        FROM t_det_prestamo
        WHERE MONTH(fecha_cobro) = %s AND YEAR(fecha_cobro) = %s
    """, (hoy.month, hoy.year), fetchone=True)
    cobrado_mes = float(resultado['total']) if resultado else 0
    
    # Total por cobrar
    resultado = query("""
        SELECT COALESCE(SUM(total_debe), 0) AS total
        FROM t_prestamo
        WHERE id_estado_prestamo = 2
    """, fetchone=True)
    total_por_cobrar = float(resultado['total']) if resultado else 0
    
    # --- Gráfico 1: Cobros por mes (últimos 12 meses) ---
    grafico_cobros = []
    for i in range(11, -1, -1):
        fecha = hoy.replace(day=1) - timedelta(days=i*30)
        mes = fecha.month
        anio = fecha.year
        r = query("""
            SELECT COALESCE(SUM(monto), 0) AS total
            FROM t_det_prestamo
            WHERE MONTH(fecha_cobro) = %s AND YEAR(fecha_cobro) = %s
        """, (mes, anio), fetchone=True)
        valor = float(r['total']) if r else 0
        grafico_cobros.append({
            'etiqueta': f"{['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'][mes-1]} {str(anio)[2:]}",
            'valor': valor
        })
    
    # --- Gráfico 2: Préstamos por mes (últimos 12 meses) ---
    grafico_prestamos = []
    for i in range(11, -1, -1):
        fecha = hoy.replace(day=1) - timedelta(days=i*30)
        mes = fecha.month
        anio = fecha.year
        r = query("""
            SELECT COALESCE(SUM(monto_prestado), 0) AS total
            FROM t_prestamo
            WHERE MONTH(fecha_prestamo) = %s AND YEAR(fecha_prestamo) = %s
        """, (mes, anio), fetchone=True)
        valor = float(r['total']) if r else 0
        grafico_prestamos.append({
            'etiqueta': f"{['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'][mes-1]} {str(anio)[2:]}",
            'valor': valor
        })
    
    # --- Ranking Cobradores ---
    ranking_cobradores = query("""
        SELECT 
            COALESCE(cb.nombre, 'Sin asignar') AS cobrador,
            COUNT(dp.id) AS total_pagos,
            COALESCE(SUM(dp.monto), 0) AS total_cobrado
        FROM t_det_prestamo dp
        LEFT JOIN t_prestamo p ON dp.id_prestamo = p.id
        LEFT JOIN t_cobrador cb ON p.id_cobrador = cb.id
        WHERE MONTH(dp.fecha_cobro) = %s AND YEAR(dp.fecha_cobro) = %s
        GROUP BY cb.nombre
        ORDER BY total_cobrado DESC
        LIMIT 10
    """, (hoy.month, hoy.year), fetchall=True) or []
    
    # --- Top Deudores ---
    top_deudores_raw = query("""
        SELECT 
            c.nombre AS cliente,
            c.dni AS cliente_dni,
            SUM(p.total_debe) AS deuda
        FROM t_prestamo p
        LEFT JOIN t_cliente c ON p.id_cliente = c.id
        WHERE p.id_estado_prestamo = 2 AND p.total_debe > 0
        GROUP BY c.id, c.nombre, c.dni
        ORDER BY deuda DESC
        LIMIT 10
    """, fetchall=True) or []
    
    max_deuda = top_deudores_raw[0]['deuda'] if top_deudores_raw else 1
    top_deudores = []
    for d in top_deudores_raw:
        porcentaje = (float(d['deuda']) / float(max_deuda) * 100) if max_deuda else 0
        top_deudores.append({
            'cliente': d['cliente'] or 'Sin nombre',
            'deuda': float(d['deuda']),
            'porcentaje': porcentaje
        })
    
    # --- Datos para el template ---
    meses_nombres = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 
                     'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    anios_disponibles = list(range(hoy.year - 3, hoy.year + 1))
    
    data_usuario = {
        'id_usuario': session.get('id'),
        'nombre_usuario': session.get('nombre'),
        'id_nivel': session.get('id_nivel')
    }
    
    data_panel = {
        'cliente_registrados': total_clientes,
        'dinero_capital': total_caja,
        'dinero_recogido': cobrado_mes,
        'total_por_cobrar': total_por_cobrar,
        'ranking_cobradores': ranking_cobradores,
        'top_deudores': top_deudores,
        'grafico_cobros': grafico_cobros,
        'grafico_prestamos': grafico_prestamos,
    }
    
    return render_template('dashboard.html',
                           usuario=data_usuario,
                           panel=data_panel,
                           ahora=hoy.strftime('%d/%m/%Y %H:%M'),
                           mes_actual=hoy.month,
                           meses_nombres=meses_nombres,
                           anios_disponibles=anios_disponibles)


# ============================================================
# RUTAS PLACEHOLDER (por ahora, se implementarán después)
# ============================================================
# ============================================================
# MÓDULO DE CLIENTES (REAL)
# ============================================================
from models.cliente import ClienteModel

@app.route('/clientes')
def clientes():
    if not session.get('logueado'):
        return redirect(url_for('login'))
    lista_clientes = ClienteModel.listar_todos()
    return render_template('clientes.html', clientes=lista_clientes)

@app.route('/cliente/nuevo', methods=['GET', 'POST'])
def cliente_nuevo():
    if not session.get('logueado'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        datos = {
            'dni': request.form.get('dni', ''),
            'nombre': request.form.get('nombre', ''),
            'nombre_negocio': request.form.get('nombre_negocio', ''),
            'telf': request.form.get('telf', ''),
            'email': request.form.get('email', ''),
            'direccion': request.form.get('direccion', ''),
            'direccion_cobro': request.form.get('direccion_cobro', ''),
            'referencia_1': request.form.get('referencia_1', ''),
            'referencia_2': request.form.get('referencia_2', ''),
            'id_tipo_estado_cliente': 1,
            'id_reputacion': 1,
            'id_documentacion': 1
        }
        ClienteModel.crear(datos)
        flash('Cliente creado correctamente', 'success')
        return redirect(url_for('clientes'))
    
    return render_template('cliente_form.html', cliente=None, titulo='Nuevo Cliente')

@app.route('/cliente/editar/<int:id_cliente>', methods=['GET', 'POST'])
def cliente_editar(id_cliente):
    if not session.get('logueado'):
        return redirect(url_for('login'))
    
    cliente = ClienteModel.obtener_por_id(id_cliente)
    if not cliente:
        flash('Cliente no encontrado', 'danger')
        return redirect(url_for('clientes'))
    
    if request.method == 'POST':
        datos = {
            'dni': request.form.get('dni', ''),
            'nombre': request.form.get('nombre', ''),
            'nombre_negocio': request.form.get('nombre_negocio', ''),
            'telf': request.form.get('telf', ''),
            'email': request.form.get('email', ''),
            'direccion': request.form.get('direccion', ''),
            'direccion_cobro': request.form.get('direccion_cobro', ''),
            'referencia_1': request.form.get('referencia_1', ''),
            'referencia_2': request.form.get('referencia_2', ''),
        }
        ClienteModel.actualizar(id_cliente, datos)
        flash('Cliente actualizado correctamente', 'success')
        return redirect(url_for('clientes'))
    
    return render_template('cliente_form.html', cliente=cliente, titulo='Editar Cliente')

@app.route('/cliente/eliminar/<int:id_cliente>')
def cliente_eliminar(id_cliente):
    if not session.get('logueado'):
        return redirect(url_for('login'))
    
    ClienteModel.eliminar(id_cliente)
    flash('Cliente eliminado correctamente', 'success')
    return redirect(url_for('clientes'))

@app.route('/codeudores')
def codeudores():
    if not session.get('logueado'):
        return redirect(url_for('login'))
    return render_template('placeholder.html', titulo='Codeudores', icono='fa-file-signature')

# ============================================================
# MÓDULO DE IMPORTACIÓN DE CONTACTOS (VCF)
# ============================================================
from models.vcf_import import VCFImportModel

UPLOAD_VCF = os.path.join(os.path.dirname(__file__), 'static', 'vcf_uploads')
os.makedirs(UPLOAD_VCF, exist_ok=True)

# Variable global temporal para guardar los contactos analizados
_contactos_temp = {}

@app.route('/importar_contactos/<tipo>', methods=['GET', 'POST'])
def importar_contactos(tipo):
    """Importar contactos desde VCF para Clientes, Usuarios, Cobradores o Socios."""
    if not session.get('logueado'):
        return redirect(url_for('login'))
    
    if tipo not in ['clientes', 'usuarios', 'cobradores', 'socios']:
        flash('Tipo de importación no válido', 'danger')
        return redirect(url_for('dashboard'))
    
    contactos = None
    stats = None
    
    if request.method == 'POST':
        archivo = request.files.get('archivo_vcf')
        if not archivo or not archivo.filename:
            flash('Debes seleccionar un archivo VCF', 'warning')
            return redirect(url_for('importar_contactos', tipo=tipo))
        
        if not archivo.filename.lower().endswith('.vcf'):
            flash('El archivo debe ser .vcf', 'danger')
            return redirect(url_for('importar_contactos', tipo=tipo))
        
        # Guardar archivo
        import time
        nombre_archivo = f"vcf_{int(time.time())}.vcf"
        ruta = os.path.join(UPLOAD_VCF, nombre_archivo)
        archivo.save(ruta)
        
        # Parsear
        contactos = VCFImportModel.leer_archivo_vcf(ruta)
        
        if not contactos:
            flash('No se encontraron contactos en el archivo', 'warning')
            return redirect(url_for('importar_contactos', tipo=tipo))
        
        # Guardar temporalmente
        session_id = session.get('id')
        _contactos_temp[session_id] = {
            'tipo': tipo,
            'contactos': contactos
        }
        
        stats = VCFImportModel.estadisticas(contactos)
        flash(f'Se encontraron {len(contactos)} contactos', 'success')
    
    return render_template('importar_contactos.html',
                           tipo=tipo,
                           contactos=contactos,
                           stats=stats,
                           titulo=f'Importar Contactos - {tipo.capitalize()}')


@app.route('/importar_contactos/<tipo>/confirmar', methods=['POST'])
def importar_contactos_confirmar(tipo):
    """Confirma e inserta los contactos seleccionados."""
    if not session.get('logueado'):
        return redirect(url_for('login'))
    
    session_id = session.get('id')
    if session_id not in _contactos_temp:
        flash('Sesión de importación expirada', 'warning')
        return redirect(url_for('importar_contactos', tipo=tipo))
    
    datos = _contactos_temp[session_id]
    contactos = datos['contactos']
    
    seleccionados = request.form.getlist('seleccionados')
    insertados = 0
    
    for idx_str in seleccionados:
        idx = int(idx_str)
        if idx >= len(contactos):
            continue
        
        contacto = contactos[idx]
        
        # Obtener datos editados del formulario
        nombre = request.form.get(f'nombre_{idx}', '').strip()
        telefono = request.form.get(f'telefono_{idx}', '').strip()
        email = request.form.get(f'email_{idx}', '').strip()
        direccion = request.form.get(f'direccion_{idx}', '').strip()
        
        if not nombre:
            continue
        
        # Insertar según el tipo
        if tipo == 'clientes':
            query("""
                INSERT INTO t_cliente 
                (id_tipo_estado_cliente, id_reputacion, dni, nombre, telf, email, direccion, direccion_cobro)
                VALUES (1, 1, %s, %s, %s, %s, %s, %s)
            """, ('', nombre, telefono, email, direccion, direccion), commit=True)
            insertados += 1
        
        elif tipo == 'cobradores':
            query("""
                INSERT INTO t_cobrador (nombre)
                VALUES (%s)
            """, (nombre,), commit=True)
            insertados += 1
        
        elif tipo == 'socios':
            query("""
                INSERT INTO t_socio (nombre)
                VALUES (%s)
            """, (nombre,), commit=True)
            insertados += 1
        
        elif tipo == 'usuarios':
            # Generar login automático
            login = nombre.lower().replace(' ', '_')[:20]
            import hashlib
            clave = hashlib.sha1('123456'.encode('utf-8')).hexdigest()
            query("""
                INSERT INTO t_usuario (id_estado_usuario, id_nivel, nombre, login, clave)
                VALUES (1, 2, %s, %s, %s)
            """, (nombre, login, clave), commit=True)
            insertados += 1
    
    # Limpiar temporal
    del _contactos_temp[session_id]
    
    flash(f'Se importaron {insertados} contactos como {tipo}', 'success')
    return redirect(url_for(tipo))
# ============================================================
# MÓDULO DE PRÉSTAMOS (REAL)
# ============================================================
from models.prestamo import PrestamoModel
from models.cliente import ClienteModel

@app.route('/prestamos')
def prestamos():
    if not session.get('logueado'):
        return redirect(url_for('login'))
    lista = PrestamoModel.listar_todos() or []  # ← Asegurar lista vacía si es None
    return render_template('prestamos.html', prestamos=lista)

@app.route('/prestamos/estado/<int:id_estado>')
def prestamos_por_estado(id_estado):
    if not session.get('logueado'):
        return redirect(url_for('login'))
    lista = PrestamoModel.listar_por_estado(id_estado)
    return render_template('prestamos.html', prestamos=lista)

@app.route('/prestamo/nuevo', methods=['GET', 'POST'])
def prestamo_nuevo():
    if not session.get('logueado'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        monto = float(request.form.get('monto_prestado', 0) or 0)
        porcentaje = float(request.form.get('porcentaje', 0) or 0)
        num_cuotas = int(request.form.get('numero_cuotas', 1) or 1)
        
        interes = monto * (porcentaje / 100)
        total = monto + interes
        monto_cuota = total / num_cuotas if num_cuotas > 0 else 0
        
        datos = {
            'id_cliente': request.form.get('id_cliente'),
            'id_cobrador': request.form.get('id_cobrador') or None,
            'id_tipo_prestamo': request.form.get('id_tipo_prestamo', 1),
            'id_metodo_pago': request.form.get('id_metodo_pago', 1),
            'porcentaje': porcentaje,
            'monto_prestado': monto,
            'interes': interes,
            'total_prestado': total,
            'numero_cuotas': num_cuotas,
            'monto_x_cuotas': monto_cuota,
            'total_debe': total,
            'fecha_prestamo': request.form.get('fecha_prestamo'),
            'id_estado_prestamo': 1  # Por Aprobar
        }
        
        PrestamoModel.crear(datos)
        flash('Préstamo creado correctamente (pendiente de aprobación)', 'success')
        return redirect(url_for('prestamos'))
    
    from datetime import date
    clientes = ClienteModel.listar_todos() or []
    cobradores = query("SELECT id, nombre FROM t_cobrador", fetchall=True) or []
    tipos = PrestamoModel.listar_tipos() or []
    metodos = PrestamoModel.listar_metodos_pago() or []
    
    return render_template('prestamo_form.html',
                           titulo='Nuevo Préstamo',
                           clientes=clientes,
                           cobradores=cobradores,
                           tipos=tipos,
                           metodos=metodos,
                           fecha_hoy=date.today().strftime('%Y-%m-%d'))
@app.route('/prestamo/editar/<int:id_prestamo>', methods=['GET', 'POST'])
def prestamo_editar(id_prestamo):
    if not session.get('logueado'):
        return redirect(url_for('login'))
    
    prestamo = PrestamoModel.obtener_por_id(id_prestamo)
    if not prestamo:
        flash('Préstamo no encontrado', 'danger')
        return redirect(url_for('prestamos'))
    
    if request.method == 'POST':
        # Solo permitimos editar cobrador, tipo de préstamo, método de pago y observación
        # (No monto, ni cuotas, ni porcentaje, porque ya está creado)
        nuevo_cobrador = request.form.get('id_cobrador') or None
        
        query("""
            UPDATE t_prestamo SET
                id_cobrador = %s,
                id_tipo_prestamo = %s,
                id_metodo_pago = %s
            WHERE id = %s
        """, (
            nuevo_cobrador,
            request.form.get('id_tipo_prestamo', 1),
            request.form.get('id_metodo_pago', 1),
            id_prestamo
        ), commit=True)
        
        flash('Préstamo actualizado correctamente', 'success')
        return redirect(url_for('prestamos'))
    
    from datetime import date
    clientes = ClienteModel.listar_todos() or []
    cobradores = query("SELECT id, nombre FROM t_cobrador", fetchall=True) or []
    tipos = PrestamoModel.listar_tipos() or []
    metodos = PrestamoModel.listar_metodos_pago() or []
    
    return render_template('prestamo_editar.html',
                           titulo=f'Editar Préstamo #{id_prestamo}',
                           prestamo=prestamo,
                           clientes=clientes,
                           cobradores=cobradores,
                           tipos=tipos,
                           metodos=metodos,
                           fecha_hoy=date.today().strftime('%Y-%m-%d'))
@app.route('/prestamo/ver/<int:id_prestamo>')
def prestamo_ver(id_prestamo):
    if not session.get('logueado'):
        return redirect(url_for('login'))
    prestamo = PrestamoModel.obtener_por_id(id_prestamo)
    pagos = PrestamoModel.listar_pagos(id_prestamo)
    if not prestamo:
        flash('Préstamo no encontrado', 'danger')
        return redirect(url_for('prestamos'))
    return render_template('prestamo_ver.html', prestamo=prestamo, pagos=pagos)

@app.route('/prestamo/aprobar/<int:id_prestamo>')
def prestamo_aprobar(id_prestamo):
    if not session.get('logueado'):
        return redirect(url_for('login'))
    
    prestamo = PrestamoModel.obtener_por_id(id_prestamo)
    if not prestamo:
        flash('Préstamo no encontrado', 'danger')
        return redirect(url_for('prestamos'))
    
    if prestamo['estado_prestamo'] != 'Por Aprobar':
        flash('Este préstamo ya fue procesado', 'warning')
        return redirect(url_for('prestamo_ver', id_prestamo=id_prestamo))
    
    # Calcular datos de aprobación
    from datetime import date, timedelta
    num_cuotas = prestamo['numero_cuotas'] or 1
    monto = float(prestamo['monto_prestado'] or 0)
    porcentaje = float(prestamo['porcentaje'] or 0)
    interes = monto * (porcentaje / 100)
    total = monto + interes
    monto_cuota = total / num_cuotas
    
    # Calcular la fecha del próximo cobro (según tipo de préstamo)
    tipo = prestamo.get('tipo_prestamo', 'Diario')
    dias_por_cuota = 1  # Diario por defecto
    if tipo == 'Semanal':
        dias_por_cuota = 7
    elif tipo == 'Quincenal':
        dias_por_cuota = 15
    elif tipo == 'Mensual':
        dias_por_cuota = 30
    
    fecha_prox_cobro = date.today() + timedelta(days=dias_por_cuota)
    
    # Actualizar el préstamo
    PrestamoModel.aprobar(id_prestamo, {
        'monto_aprobado': monto,
        'porcentaje_aprobado': porcentaje,
        'interes': interes,
        'total_prestado': total,
        'total_debe': total,
        'numero_cuotas_aprobadas': num_cuotas,
        'monto_x_cuotas': monto_cuota,
        'fecha_prox_cobro': fecha_prox_cobro.strftime('%Y-%m-%d'),
        'observacion': 'Préstamo aprobado automáticamente'
    })
    
    flash('¡Préstamo aprobado correctamente! Ya está activo.', 'success')
    return redirect(url_for('prestamo_ver', id_prestamo=id_prestamo))


@app.route('/prestamo/pago/<int:id_prestamo>', methods=['GET', 'POST'])
def prestamo_pago(id_prestamo):
    if not session.get('logueado'):
        return redirect(url_for('login'))
    
    prestamo = PrestamoModel.obtener_por_id(id_prestamo)
    if not prestamo:
        flash('Préstamo no encontrado', 'danger')
        return redirect(url_for('prestamos'))
    
    if request.method == 'POST':
        monto_pago = float(request.form.get('monto', 0) or 0)
        
        if monto_pago <= 0:
            flash('El monto debe ser mayor que cero', 'danger')
            return redirect(url_for('prestamo_pago', id_prestamo=id_prestamo))
        
        # Calcular la fecha del próximo cobro (mantener el ciclo)
        from datetime import date, timedelta
        tipo = prestamo.get('tipo_prestamo', 'Diario')
        dias_por_cuota = 1
        if tipo == 'Semanal':
            dias_por_cuota = 7
        elif tipo == 'Quincenal':
            dias_por_cuota = 15
        elif tipo == 'Mensual':
            dias_por_cuota = 30
        
        fecha_prox_cobro = date.today() + timedelta(days=dias_por_cuota)
        
        # Registrar el pago
        PrestamoModel.registrar_pago(id_prestamo, {
            'id_tipo_prestamo_2': 2,  # Pago de Cuota
            'cuota': (prestamo['cuotas_amortizadas'] or 0) + 1,
            'descripcion': request.form.get('descripcion', 'Pago Efectuado'),
            'monto': monto_pago,
            'fecha_cobro': date.today().strftime('%Y-%m-%d'),
            'fecha_prox_cobro': fecha_prox_cobro.strftime('%Y-%m-%d')
        })
        
        flash(f'Pago de {monto_pago:.2f} registrado correctamente.', 'success')
        return redirect(url_for('prestamo_ver', id_prestamo=id_prestamo))
    
    from datetime import date
    return render_template('prestamo_pago.html', 
                           prestamo=prestamo, 
                           fecha_hoy=date.today().strftime('%Y-%m-%d'))
@app.route('/prestamo/eliminar/<int:id_prestamo>')
def prestamo_eliminar(id_prestamo):
    if not session.get('logueado'):
        return redirect(url_for('login'))
    PrestamoModel.eliminar(id_prestamo)
    flash('Préstamo eliminado correctamente', 'success')
    return redirect(url_for('prestamos'))

# ============================================================
# MÓDULO DE ESCANEO DE COMPROBANTES
# ============================================================
from models.comprobante import ComprobanteModel

UPLOAD_COMPROBANTES = os.path.join(os.path.dirname(__file__), 'static', 'comprobantes')
os.makedirs(UPLOAD_COMPROBANTES, exist_ok=True)

@app.route('/prestamo/escanear/<int:id_prestamo>', methods=['GET', 'POST'])
def prestamo_escanear(id_prestamo):
    if not session.get('logueado'):
        return redirect(url_for('login'))
    
    prestamo = PrestamoModel.obtener_por_id(id_prestamo)
    if not prestamo:
        flash('Préstamo no encontrado', 'danger')
        return redirect(url_for('prestamos'))
    
    datos_extraidos = None
    
    if request.method == 'POST':
        tipo = request.form.get('tipo', 'envio')
        archivo = request.files.get('comprobante')
        
        if not archivo or not archivo.filename:
            flash('Debes seleccionar una imagen', 'warning')
            return redirect(url_for('prestamo_escanear', id_prestamo=id_prestamo))
        
        # Validar extensión
        ext = archivo.filename.rsplit('.', 1)[-1].lower()
        if ext not in ['png', 'jpg', 'jpeg']:
            flash('Formato no permitido. Usa PNG, JPG o JPEG.', 'danger')
            return redirect(url_for('prestamo_escanear', id_prestamo=id_prestamo))
        
        # Guardar la imagen
        import time
        nombre_archivo = f"comprobante_{id_prestamo}_{int(time.time())}.{ext}"
        ruta = os.path.join(UPLOAD_COMPROBANTES, nombre_archivo)
        archivo.save(ruta)
        
        # Procesar con OCR y QR (pasando el tipo)
        datos_extraidos = ComprobanteModel.procesar_comprobante(ruta, tipo=tipo)
        datos_extraidos['ruta_imagen'] = f"/static/comprobantes/{nombre_archivo}"
        
        if datos_extraidos['exito']:
            tipo_texto = 'Envío' if tipo == 'envio' else 'Pago'
            flash(f"Comprobante de {tipo_texto} procesado. Monto: ${datos_extraidos['monto']:,.0f}", 'success')
        else:
            flash('Comprobante procesado pero no se detectó el monto. Verifica manualmente.', 'warning')
    
    from datetime import date
    return render_template('prestamo_escanear.html',
                           prestamo=prestamo,
                           datos=datos_extraidos,
                           fecha_hoy=date.today().strftime('%Y-%m-%d'))

# ============================================================
# MÓDULO DE COBRADORES (REAL)
# ============================================================
from models.cobrador import CobradorModel

@app.route('/cobradores')
def cobradores():
    if not session.get('logueado'):
        return redirect(url_for('login'))
    lista = CobradorModel.listar_todos()
    return render_template('cobradores.html', cobradores=lista)

@app.route('/cobrador/nuevo', methods=['GET', 'POST'])
def cobrador_nuevo():
    if not session.get('logueado'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        datos = {
            'id_usuario': request.form.get('id_usuario') or None,
            'nombre': request.form.get('nombre', '')
        }
        CobradorModel.crear(datos)
        flash('Cobrador creado correctamente', 'success')
        return redirect(url_for('cobradores'))
    
    usuarios = CobradorModel.listar_usuarios_disponibles() or []
    return render_template('cobrador_form.html',
                           cobrador=None,
                           usuarios=usuarios,
                           titulo='Nuevo Cobrador')

@app.route('/cobrador/editar/<int:id_cobrador>', methods=['GET', 'POST'])
def cobrador_editar(id_cobrador):
    if not session.get('logueado'):
        return redirect(url_for('login'))
    
    cobrador = CobradorModel.obtener_por_id(id_cobrador)
    if not cobrador:
        flash('Cobrador no encontrado', 'danger')
        return redirect(url_for('cobradores'))
    
    if request.method == 'POST':
        datos = {
            'id_usuario': request.form.get('id_usuario') or None,
            'nombre': request.form.get('nombre', '')
        }
        CobradorModel.actualizar(id_cobrador, datos)
        flash('Cobrador actualizado correctamente', 'success')
        return redirect(url_for('cobradores'))
    
    usuarios = CobradorModel.listar_usuarios_disponibles() or []
    return render_template('cobrador_form.html',
                           cobrador=cobrador,
                           usuarios=usuarios,
                           titulo=f'Editar Cobrador #{id_cobrador}')

@app.route('/cobrador/eliminar/<int:id_cobrador>')
def cobrador_eliminar(id_cobrador):
    if not session.get('logueado'):
        return redirect(url_for('login'))
    CobradorModel.eliminar(id_cobrador)
    flash('Cobrador eliminado correctamente', 'success')
    return redirect(url_for('cobradores'))

# ============================================================
# MÓDULO DE SOCIOS (REAL)
# ============================================================
from models.socio import SocioModel

@app.route('/socios')
def socios():
    if not session.get('logueado'):
        return redirect(url_for('login'))
    lista = SocioModel.listar_todos()
    return render_template('socios.html', socios=lista)

@app.route('/socio/nuevo', methods=['GET', 'POST'])
def socio_nuevo():
    if not session.get('logueado'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        datos = {
            'id_usuario': request.form.get('id_usuario') or None,
            'nombre': request.form.get('nombre', '')
        }
        SocioModel.crear(datos)
        flash('Socio creado correctamente', 'success')
        return redirect(url_for('socios'))
    
    usuarios = SocioModel.listar_usuarios_disponibles() or []
    return render_template('socio_form.html',
                           socio=None,
                           usuarios=usuarios,
                           titulo='Nuevo Socio')

@app.route('/socio/editar/<int:id_socio>', methods=['GET', 'POST'])
def socio_editar(id_socio):
    if not session.get('logueado'):
        return redirect(url_for('login'))
    
    socio = SocioModel.obtener_por_id(id_socio)
    if not socio:
        flash('Socio no encontrado', 'danger')
        return redirect(url_for('socios'))
    
    if request.method == 'POST':
        datos = {
            'id_usuario': request.form.get('id_usuario') or None,
            'nombre': request.form.get('nombre', '')
        }
        SocioModel.actualizar(id_socio, datos)
        flash('Socio actualizado correctamente', 'success')
        return redirect(url_for('socios'))
    
    usuarios = SocioModel.listar_usuarios_disponibles() or []
    return render_template('socio_form.html',
                           socio=socio,
                           usuarios=usuarios,
                           titulo=f'Editar Socio #{id_socio}')

@app.route('/socio/eliminar/<int:id_socio>')
def socio_eliminar(id_socio):
    if not session.get('logueado'):
        return redirect(url_for('login'))
    SocioModel.eliminar(id_socio)
    flash('Socio eliminado correctamente', 'success')
    return redirect(url_for('socios'))

# ============================================================
# MÓDULO DE ZONAS (REAL)
# ============================================================
from models.zona import ZonaModel, ZonaCobradorModel

@app.route('/zonas')
def zonas():
    if not session.get('logueado'):
        return redirect(url_for('login'))
    lista = ZonaModel.listar_todas() or []
    asignaciones = ZonaCobradorModel.listar_todas() or []
    total_asignaciones = ZonaCobradorModel.contar()
    return render_template('zonas.html',
                           zonas=lista,
                           asignaciones=asignaciones,
                           total_asignaciones=total_asignaciones)

@app.route('/zona/nueva', methods=['GET', 'POST'])
def zona_nueva():
    if not session.get('logueado'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        datos = {
            'zona': request.form.get('zona', ''),
            'direccion': request.form.get('direccion', '')
        }
        ZonaModel.crear(datos)
        flash('Zona creada correctamente', 'success')
        return redirect(url_for('zonas'))
    
    return render_template('zona_form.html', zona=None, titulo='Nueva Zona')

@app.route('/zona/editar/<int:id_zona>', methods=['GET', 'POST'])
def zona_editar(id_zona):
    if not session.get('logueado'):
        return redirect(url_for('login'))
    
    zona = ZonaModel.obtener_por_id(id_zona)
    if not zona:
        flash('Zona no encontrada', 'danger')
        return redirect(url_for('zonas'))
    
    if request.method == 'POST':
        datos = {
            'zona': request.form.get('zona', ''),
            'direccion': request.form.get('direccion', '')
        }
        ZonaModel.actualizar(id_zona, datos)
        flash('Zona actualizada correctamente', 'success')
        return redirect(url_for('zonas'))
    
    return render_template('zona_form.html', zona=zona, titulo=f'Editar Zona #{id_zona}')

@app.route('/zona/eliminar/<int:id_zona>')
def zona_eliminar(id_zona):
    if not session.get('logueado'):
        return redirect(url_for('login'))
    ZonaModel.eliminar(id_zona)
    flash('Zona eliminada correctamente', 'success')
    return redirect(url_for('zonas'))

# --- Asignaciones Zona-Cobrador ---

@app.route('/zona/asignacion/nueva', methods=['GET', 'POST'])
def asignacion_nueva():
    if not session.get('logueado'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        datos = {
            'id_zona': request.form.get('id_zona'),
            'id_cobrador': request.form.get('id_cobrador'),
            'id_sucursal': request.form.get('id_sucursal')
        }
        ZonaCobradorModel.crear(datos)
        flash('Asignación creada correctamente', 'success')
        return redirect(url_for('zonas'))
    
    zonas_lista = ZonaModel.listar_todas() or []
    cobradores_lista = query("SELECT id, nombre FROM t_cobrador ORDER BY nombre", fetchall=True) or []
    sucursales_lista = query("SELECT id, descripcion FROM t_sucursal ORDER BY descripcion", fetchall=True) or []
    
    return render_template('asignacion_form.html',
                           asignacion=None,
                           zonas=zonas_lista,
                           cobradores=cobradores_lista,
                           sucursales=sucursales_lista,
                           titulo='Nueva Asignación')

@app.route('/zona/asignacion/editar/<int:id_asignacion>', methods=['GET', 'POST'])
def asignacion_editar(id_asignacion):
    if not session.get('logueado'):
        return redirect(url_for('login'))
    
    asignacion = ZonaCobradorModel.obtener_por_id(id_asignacion)
    if not asignacion:
        flash('Asignación no encontrada', 'danger')
        return redirect(url_for('zonas'))
    
    if request.method == 'POST':
        datos = {
            'id_zona': request.form.get('id_zona'),
            'id_cobrador': request.form.get('id_cobrador'),
            'id_sucursal': request.form.get('id_sucursal')
        }
        ZonaCobradorModel.actualizar(id_asignacion, datos)
        flash('Asignación actualizada correctamente', 'success')
        return redirect(url_for('zonas'))
    
    zonas_lista = ZonaModel.listar_todas() or []
    cobradores_lista = query("SELECT id, nombre FROM t_cobrador ORDER BY nombre", fetchall=True) or []
    sucursales_lista = query("SELECT id, descripcion FROM t_sucursal ORDER BY descripcion", fetchall=True) or []
    
    return render_template('asignacion_form.html',
                           asignacion=asignacion,
                           zonas=zonas_lista,
                           cobradores=cobradores_lista,
                           sucursales=sucursales_lista,
                           titulo=f'Editar Asignación #{id_asignacion}')

@app.route('/zona/asignacion/eliminar/<int:id_asignacion>')
def asignacion_eliminar(id_asignacion):
    if not session.get('logueado'):
        return redirect(url_for('login'))
    ZonaCobradorModel.eliminar(id_asignacion)
    flash('Asignación eliminada correctamente', 'success')
    return redirect(url_for('zonas'))

# ============================================================
# MÓDULO DE CAJA (REAL)
# ============================================================
from models.caja import CajaModel

@app.route('/caja')
def caja():
    if not session.get('logueado'):
        return redirect(url_for('login'))
    
    caja_principal = CajaModel.obtener_caja_principal()
    if not caja_principal:
        flash('No hay cajas configuradas. Contacta al administrador.', 'warning')
        return redirect(url_for('dashboard'))
    
    movimientos = CajaModel.listar_movimientos(caja_principal['id_caja']) or []
    total_ingresos = CajaModel.sumar_ingresos()
    total_egresos = CajaModel.sumar_egresos()
    
    return render_template('caja.html',
                           caja=caja_principal,
                           movimientos=movimientos,
                           total_ingresos=total_ingresos,
                           total_egresos=total_egresos)

@app.route('/caja/nuevo', methods=['GET', 'POST'])
def caja_nuevo_movimiento():
    if not session.get('logueado'):
        return redirect(url_for('login'))
    
    caja_principal = CajaModel.obtener_caja_principal()
    if not caja_principal:
        flash('No hay cajas configuradas.', 'warning')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        id_tipo_ingreso = request.form.get('id_tipo_ingreso')
        monto = float(request.form.get('monto', 0) or 0)
        fecha = request.form.get('fecha')
        
        if monto <= 0:
            flash('El monto debe ser mayor que cero', 'danger')
            return redirect(url_for('caja_nuevo_movimiento'))
        
        CajaModel.registrar_movimiento(
            caja_principal['id_caja'],
            id_tipo_ingreso,
            monto,
            fecha
        )
        
        flash('Movimiento registrado correctamente', 'success')
        return redirect(url_for('caja'))
    
    from datetime import date
    tipos = CajaModel.listar_tipos_movimiento() or []
    return render_template('caja_movimiento.html',
                           caja=caja_principal,
                           tipos=tipos,
                           fecha_hoy=date.today().strftime('%Y-%m-%d'))

@app.route('/caja/editar/<int:id_movimiento>', methods=['GET', 'POST'])
def caja_editar_movimiento(id_movimiento):
    if not session.get('logueado'):
        return redirect(url_for('login'))
    
    caja_principal = CajaModel.obtener_caja_principal()
    if not caja_principal:
        flash('No hay cajas configuradas.', 'warning')
        return redirect(url_for('dashboard'))
    
    movimiento = CajaModel.obtener_movimiento_por_id(id_movimiento)
    if not movimiento:
        flash('Movimiento no encontrado', 'danger')
        return redirect(url_for('caja'))
    
    if request.method == 'POST':
        id_tipo_ingreso = request.form.get('id_tipo_ingreso')
        monto = float(request.form.get('monto', 0) or 0)
        fecha = request.form.get('fecha')
        
        if monto <= 0:
            flash('El monto debe ser mayor que cero', 'danger')
            return redirect(url_for('caja_editar_movimiento', id_movimiento=id_movimiento))
        
        CajaModel.actualizar_movimiento(id_movimiento, caja_principal['id_caja'], {
            'id_tipo_ingreso': id_tipo_ingreso,
            'monto': monto,
            'fecha': fecha
        })
        
        flash('Movimiento actualizado correctamente', 'success')
        return redirect(url_for('caja'))
    
    tipos = CajaModel.listar_tipos_movimiento() or []
    return render_template('caja_editar_movimiento.html',
                           caja=caja_principal,
                           movimiento=movimiento,
                           tipos=tipos)

@app.route('/caja/eliminar/<int:id_movimiento>')
def caja_eliminar_movimiento(id_movimiento):
    if not session.get('logueado'):
        return redirect(url_for('login'))
    
    caja_principal = CajaModel.obtener_caja_principal()
    if not caja_principal:
        flash('No hay cajas configuradas.', 'warning')
        return redirect(url_for('dashboard'))
    
    CajaModel.eliminar_movimiento(id_movimiento, caja_principal['id_caja'])
    flash('Movimiento eliminado correctamente', 'success')
    return redirect(url_for('caja'))

# ============================================================
# MÓDULO DE CAPITAL (REAL)
# ============================================================
from models.capital import CapitalModel

@app.route('/capital')
def capital():
    if not session.get('logueado'):
        return redirect(url_for('login'))
    
    # Asegurar que exista el registro de capital
    cap = CapitalModel.obtener_capital()
    if not cap:
        CapitalModel.inicializar_capital()
        cap = CapitalModel.obtener_capital()
    
    aportes = CapitalModel.listar_aportes() or []
    
    return render_template('capital.html',
                           capital=cap,
                           aportes=aportes)

@app.route('/capital/nuevo', methods=['GET', 'POST'])
def capital_nuevo_aporte():
    if not session.get('logueado'):
        return redirect(url_for('login'))
    
    cap = CapitalModel.obtener_capital()
    if not cap:
        CapitalModel.inicializar_capital()
        cap = CapitalModel.obtener_capital()
    
    if request.method == 'POST':
        id_socio = request.form.get('id_socio')
        monto = float(request.form.get('monto', 0) or 0)
        descripcion = request.form.get('descripcion', '')
        
        if monto <= 0:
            flash('El monto debe ser mayor que cero', 'danger')
            return redirect(url_for('capital_nuevo_aporte'))
        
        CapitalModel.registrar_aporte(cap['id'], id_socio, descripcion, monto)
        flash('Aporte registrado correctamente', 'success')
        return redirect(url_for('capital'))
    
    socios = CapitalModel.listar_socios() or []
    return render_template('capital_aporte.html',
                           capital=cap,
                           aporte=None,
                           socios=socios,
                           titulo='Nuevo Aporte de Capital')

@app.route('/capital/editar/<int:id_aporte>', methods=['GET', 'POST'])
def capital_editar_aporte(id_aporte):
    if not session.get('logueado'):
        return redirect(url_for('login'))
    
    cap = CapitalModel.obtener_capital()
    aporte = CapitalModel.obtener_aporte_por_id(id_aporte)
    
    if not aporte:
        flash('Aporte no encontrado', 'danger')
        return redirect(url_for('capital'))
    
    if request.method == 'POST':
        id_socio = request.form.get('id_socio')
        monto = float(request.form.get('monto', 0) or 0)
        descripcion = request.form.get('descripcion', '')
        
        if monto <= 0:
            flash('El monto debe ser mayor que cero', 'danger')
            return redirect(url_for('capital_editar_aporte', id_aporte=id_aporte))
        
        CapitalModel.actualizar_aporte(id_aporte, monto, descripcion, id_socio)
        flash('Aporte actualizado correctamente', 'success')
        return redirect(url_for('capital'))
    
    socios = CapitalModel.listar_socios() or []
    return render_template('capital_aporte.html',
                           capital=cap,
                           aporte=aporte,
                           socios=socios,
                           titulo=f'Editar Aporte #{id_aporte}')

@app.route('/capital/eliminar/<int:id_aporte>')
def capital_eliminar_aporte(id_aporte):
    if not session.get('logueado'):
        return redirect(url_for('login'))
    
    CapitalModel.eliminar_aporte(id_aporte)
    flash('Aporte eliminado correctamente', 'success')
    return redirect(url_for('capital'))

# ============================================================
# MÓDULO DE GASTOS (REAL)
# ============================================================
from models.gasto import GastoModel

@app.route('/gastos')
def gastos():
    if not session.get('logueado'):
        return redirect(url_for('login'))
    lista = GastoModel.listar_todos()
    total_gastos = GastoModel.sumar_total()
    total_registros = GastoModel.contar()
    return render_template('gastos.html',
                           gastos=lista,
                           total_gastos=total_gastos,
                           total_registros=total_registros)

@app.route('/gasto/nuevo', methods=['GET', 'POST'])
def gasto_nuevo():
    if not session.get('logueado'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        id_cobrador = request.form.get('id_cobrador') or None
        fecha = request.form.get('fecha')
        
        tipos = request.form.getlist('tipo_gasto[]')
        descripciones = request.form.getlist('descripcion[]')
        cantidades = request.form.getlist('cantidad[]')
        montos = request.form.getlist('monto[]')
        
        detalles = []
        for i in range(len(tipos)):
            if tipos[i]:
                detalles.append({
                    'id_tipo_gasto': tipos[i],
                    'descripcion': descripciones[i] if i < len(descripciones) else '',
                    'cantidad': int(cantidades[i]) if i < len(cantidades) and cantidades[i] else 1,
                    'monto': float(montos[i]) if i < len(montos) and montos[i] else 0
                })
        
        if not detalles:
            flash('Debe agregar al menos un ítem al gasto', 'danger')
            return redirect(url_for('gasto_nuevo'))
        
        GastoModel.crear(id_cobrador, fecha, detalles)
        flash('Gasto registrado correctamente', 'success')
        return redirect(url_for('gastos'))
    
    from datetime import date
    tipos = GastoModel.listar_tipos_gasto() or []
    cobradores = GastoModel.listar_cobradores() or []
    return render_template('gasto_form.html',
                           titulo='Nuevo Gasto',
                           gasto=None,
                           tipos=tipos,
                           cobradores=cobradores,
                           fecha_hoy=date.today().strftime('%Y-%m-%d'))

@app.route('/gasto/ver/<int:id_gasto>')
def gasto_ver(id_gasto):
    if not session.get('logueado'):
        return redirect(url_for('login'))
    gasto = GastoModel.obtener_por_id(id_gasto)
    if not gasto:
        flash('Gasto no encontrado', 'danger')
        return redirect(url_for('gastos'))
    return render_template('gasto_ver.html', gasto=gasto)

@app.route('/gasto/editar/<int:id_gasto>', methods=['GET', 'POST'])
def gasto_editar(id_gasto):
    if not session.get('logueado'):
        return redirect(url_for('login'))
    
    gasto = GastoModel.obtener_por_id(id_gasto)
    if not gasto:
        flash('Gasto no encontrado', 'danger')
        return redirect(url_for('gastos'))
    
    if request.method == 'POST':
        id_cobrador = request.form.get('id_cobrador') or None
        fecha = request.form.get('fecha')
        
        tipos = request.form.getlist('tipo_gasto[]')
        descripciones = request.form.getlist('descripcion[]')
        cantidades = request.form.getlist('cantidad[]')
        montos = request.form.getlist('monto[]')
        
        detalles = []
        for i in range(len(tipos)):
            if tipos[i]:
                detalles.append({
                    'id_tipo_gasto': tipos[i],
                    'descripcion': descripciones[i] if i < len(descripciones) else '',
                    'cantidad': int(cantidades[i]) if i < len(cantidades) and cantidades[i] else 1,
                    'monto': float(montos[i]) if i < len(montos) and montos[i] else 0
                })
        
        if not detalles:
            flash('Debe agregar al menos un ítem al gasto', 'danger')
            return redirect(url_for('gasto_editar', id_gasto=id_gasto))
        
        GastoModel.actualizar(id_gasto, id_cobrador, fecha, detalles)
        flash('Gasto actualizado correctamente', 'success')
        return redirect(url_for('gastos'))
    
    tipos = GastoModel.listar_tipos_gasto() or []
    cobradores = GastoModel.listar_cobradores() or []
    return render_template('gasto_form.html',
                           titulo=f'Editar Gasto #{id_gasto}',
                           gasto=gasto,
                           tipos=tipos,
                           cobradores=cobradores,
                           fecha_hoy=gasto['fecha'])

@app.route('/gasto/eliminar/<int:id_gasto>')
def gasto_eliminar(id_gasto):
    if not session.get('logueado'):
        return redirect(url_for('login'))
    GastoModel.eliminar(id_gasto)
    flash('Gasto eliminado correctamente', 'success')
    return redirect(url_for('gastos'))

# ============================================================
# MÓDULO DE CIERRE POR DÍA (REAL)
# ============================================================
from models.cierre import CierreModel

@app.route('/cierre', methods=['GET', 'POST'])
def cierre():
    if not session.get('logueado'):
        return redirect(url_for('login'))
    
    # Fecha seleccionada (por defecto hoy)
    fecha = request.args.get('fecha') or request.form.get('fecha')
    if not fecha:
        from datetime import date
        fecha = date.today().strftime('%Y-%m-%d')
    
    if request.method == 'POST':
        monto = float(request.form.get('monto', 0) or 0)
        monto_recibido = float(request.form.get('monto_recibido', 0) or 0)
        total = float(request.form.get('total', 0) or 0)
        observaciones = request.form.get('observaciones', '')
        
        CierreModel.crear({
            'monto': monto,
            'monto_recibido': monto_recibido,
            'total': total,
            'observaciones': observaciones,
            'fecha': fecha
        })
        
        flash(f'Cierre del {fecha} registrado correctamente', 'success')
        return redirect(url_for('cierre', fecha=fecha))
    
    # Calcular datos del día
    total_cobrado = CierreModel.total_cobrado_dia(fecha)
    total_gastos = CierreModel.total_gastos_dia(fecha)
    pagos_dia = CierreModel.contar_pagos_dia(fecha)
    prestamos_dia = CierreModel.contar_prestamos_dia(fecha)
    neto_dia = total_cobrado - total_gastos
    ya_cerrado = CierreModel.existe_cierre(fecha)
    
    cierres = CierreModel.listar_todos() or []
    
    return render_template('cierre.html',
                           fecha=fecha,
                           total_cobrado=total_cobrado,
                           total_gastos=total_gastos,
                           pagos_dia=pagos_dia,
                           prestamos_dia=prestamos_dia,
                           neto_dia=neto_dia,
                           ya_cerrado=ya_cerrado,
                           cierres=cierres)

@app.route('/cierre/eliminar/<int:id_cierre>')
def cierre_eliminar(id_cierre):
    if not session.get('logueado'):
        return redirect(url_for('login'))
    CierreModel.eliminar(id_cierre)
    flash('Cierre eliminado correctamente', 'success')
    return redirect(url_for('cierre'))
# ============================================================
# MÓDULO DE EMPRESA (REAL con subida de logo)
# ============================================================
from models.empresa import EmpresaModel
from werkzeug.utils import secure_filename

# Configuración de subida de archivos
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'img')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/empresa', methods=['GET', 'POST'])
def empresa():
    if not session.get('logueado'):
        return redirect(url_for('login'))
    
    emp = EmpresaModel.inicializar()
    
    if request.method == 'POST':
        datos = {
            'nombre': request.form.get('nombre', ''),
            'nit': request.form.get('nit', ''),
            'direccion': request.form.get('direccion', ''),
            'telefono': request.form.get('telefono', ''),
            'email': request.form.get('email', ''),
            'logo': emp['logo'] if emp else ''
        }
        
        # Procesar la subida del logo
        archivo = request.files.get('logo_archivo')
        if archivo and archivo.filename:
            if allowed_file(archivo.filename):
                # Generar nombre único para evitar colisiones
                import time
                ext = archivo.filename.rsplit('.', 1)[1].lower()
                nombre_archivo = f"logo_empresa_{int(time.time())}.{ext}"
                ruta_completa = os.path.join(UPLOAD_FOLDER, nombre_archivo)
                archivo.save(ruta_completa)
                
                # Guardar la ruta relativa para mostrarla en el template
                datos['logo'] = f"/static/img/{nombre_archivo}"
                flash('Logo subido correctamente', 'success')
            else:
                flash('Formato de imagen no permitido. Usa PNG, JPG, JPEG o GIF.', 'danger')
                return redirect(url_for('empresa'))
        
        EmpresaModel.actualizar(emp['id'], datos)
        flash('Datos de la empresa actualizados correctamente', 'success')
        return redirect(url_for('empresa'))
    
    return render_template('empresa.html', empresa=emp)

# ============================================================
# MÓDULO DE USUARIOS (REAL)
# ============================================================
from models.usuario import UsuarioModel
import hashlib

@app.route('/usuarios')
def usuarios():
    if not session.get('logueado'):
        return redirect(url_for('login'))
    lista = UsuarioModel.listar_todos()
    return render_template('usuarios.html', usuarios=lista)

@app.route('/usuario/nuevo', methods=['GET', 'POST'])
def usuario_nuevo():
    if not session.get('logueado'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        nombre = request.form.get('nombre', '')
        login = request.form.get('login', '')
        clave = request.form.get('clave', '')
        id_nivel = request.form.get('id_nivel', 1)
        id_estado_usuario = request.form.get('id_estado_usuario', 1)
        
        if not nombre or not login or not clave:
            flash('Nombre, login y contraseña son obligatorios', 'danger')
            return redirect(url_for('usuario_nuevo'))
        
        if UsuarioModel.existe_login(login):
            flash('Ese login ya está en uso', 'danger')
            return redirect(url_for('usuario_nuevo'))
        
        # Hash SHA-1
        clave_hash = hashlib.sha1(clave.encode('utf-8')).hexdigest()
        
        datos = {
            'nombre': nombre,
            'login': login,
            'clave': clave_hash,
            'id_nivel': id_nivel,
            'id_estado_usuario': id_estado_usuario
        }
        
        UsuarioModel.crear(datos)
        flash('Usuario creado correctamente', 'success')
        return redirect(url_for('usuarios'))
    
    niveles = UsuarioModel.listar_niveles() or []
    estados = UsuarioModel.listar_estados() or []
    return render_template('usuario_form.html',
                           usuario=None,
                           niveles=niveles,
                           estados=estados,
                           titulo='Nuevo Usuario')

@app.route('/usuario/editar/<int:id_usuario>', methods=['GET', 'POST'])
def usuario_editar(id_usuario):
    if not session.get('logueado'):
        return redirect(url_for('login'))
    
    usuario = UsuarioModel.obtener_por_id(id_usuario)
    if not usuario:
        flash('Usuario no encontrado', 'danger')
        return redirect(url_for('usuarios'))
    
    if request.method == 'POST':
        nombre = request.form.get('nombre', '')
        login = request.form.get('login', '')
        clave = request.form.get('clave', '')
        id_nivel = request.form.get('id_nivel', 1)
        id_estado_usuario = request.form.get('id_estado_usuario', 1)
        
        if not nombre or not login:
            flash('Nombre y login son obligatorios', 'danger')
            return redirect(url_for('usuario_editar', id_usuario=id_usuario))
        
        if UsuarioModel.existe_login(login, excluir_id=id_usuario):
            flash('Ese login ya está en uso por otro usuario', 'danger')
            return redirect(url_for('usuario_editar', id_usuario=id_usuario))
        
        # Si no se cambió la contraseña, mantener la actual
        if clave:
            clave_hash = hashlib.sha1(clave.encode('utf-8')).hexdigest()
        else:
            clave_hash = usuario['clave']
        
        datos = {
            'nombre': nombre,
            'login': login,
            'clave': clave_hash,
            'id_nivel': id_nivel,
            'id_estado_usuario': id_estado_usuario
        }
        
        UsuarioModel.actualizar(id_usuario, datos)
        flash('Usuario actualizado correctamente', 'success')
        return redirect(url_for('usuarios'))
    
    niveles = UsuarioModel.listar_niveles() or []
    estados = UsuarioModel.listar_estados() or []
    return render_template('usuario_form.html',
                           usuario=usuario,
                           niveles=niveles,
                           estados=estados,
                           titulo=f'Editar Usuario #{id_usuario}')

@app.route('/usuario/eliminar/<int:id_usuario>')
def usuario_eliminar(id_usuario):
    if not session.get('logueado'):
        return redirect(url_for('login'))
    
    if id_usuario == session.get('id'):
        flash('No puedes eliminar tu propio usuario', 'danger')
        return redirect(url_for('usuarios'))
    
    UsuarioModel.eliminar(id_usuario)
    flash('Usuario eliminado correctamente', 'success')
    return redirect(url_for('usuarios'))

# ============================================================
# MÓDULO DE REPORTES (REAL)
# ============================================================
from models.reporte import ReporteModel
from datetime import date, timedelta

@app.route('/reportes')
def reportes():
    if not session.get('logueado'):
        return redirect(url_for('login'))
    
    # Fechas por defecto: último mes
    hoy = date.today()
    hace_un_mes = hoy - timedelta(days=30)
    
    fecha_i = request.args.get('fecha_i', hace_un_mes.strftime('%Y-%m-%d'))
    fecha_f = request.args.get('fecha_f', hoy.strftime('%Y-%m-%d'))
    
    prestamos = ReporteModel.prestamos_por_fecha(fecha_i, fecha_f) or []
    cobros = ReporteModel.cobros_por_fecha(fecha_i, fecha_f) or []
    gastos = ReporteModel.gastos_por_fecha(fecha_i, fecha_f) or []
    
    resumen_prestamos = ReporteModel.resumen_prestamos(fecha_i, fecha_f) or {}
    resumen_cobros = ReporteModel.resumen_cobros(fecha_i, fecha_f) or {}
    resumen_gastos = ReporteModel.resumen_gastos(fecha_i, fecha_f) or {}
    
    prestamos_cobrador = ReporteModel.prestamos_por_cobrador(fecha_i, fecha_f) or []
    cobros_cobrador = ReporteModel.cobros_por_cobrador(fecha_i, fecha_f) or []
    
    return render_template('reportes.html',
                           fecha_i=fecha_i,
                           fecha_f=fecha_f,
                           prestamos=prestamos,
                           cobros=cobros,
                           gastos=gastos,
                           resumen_prestamos=resumen_prestamos,
                           resumen_cobros=resumen_cobros,
                           resumen_gastos=resumen_gastos,
                           prestamos_cobrador=prestamos_cobrador,
                           cobros_cobrador=cobros_cobrador)

@app.route('/logout')
def logout():
    """Cerrar sesión."""
    session.clear()
    return redirect(url_for('login'))


# ============================================================
# INICIAR SERVIDOR AUTOMÁTICAMENTE
# ============================================================
if __name__ == '__main__':
    ip_local = obtener_ip_local()
    
    print("=" * 60)
    print("  SISTEMA PAGADIARIO - VERSIÓN PYTHON (Flask)")
    print("=" * 60)
    print(f"  Servidor corriendo en:  http://0.0.0.0:5000")
    print(f"  Abre desde tu celular:  http://{ip_local}:5000")
    print(f"  Abre desde otra PC:     http://{ip_local}:5000")
    print("=" * 60)
    print("  Presiona CTRL+C para detener el servidor")
    print("=" * 60)
    
    # Abrir el navegador automáticamente después de 2 segundos
    threading.Timer(2.0, abrir_navegador, args=[ip_local]).start()
    
    # Iniciar Flask en el puerto 5000 (libre)
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
  