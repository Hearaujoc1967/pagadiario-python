# actualizar_sidebars.py
"""
Script para actualizar automáticamente el sidebar en TODOS los templates.
Reemplaza el bloque <div class="sidebar">...</div> por {% include '_sidebar.html' %}
"""
import os
import re

# Ruta de la carpeta de templates
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'templates')

# Patrón regex para encontrar el bloque completo del sidebar
PATRON_SIDEBAR = re.compile(
    r'<div\s+class="sidebar"[^>]*>.*?</div>\s*(?=\s*<!--|\s*<div\s+class="main-content"|\s*$)',
    re.DOTALL | re.IGNORECASE
)

REEMPLAZO = "{% include '_sidebar.html' %}"

def procesar_archivo(ruta):
    """Procesa un solo archivo HTML."""
    try:
        with open(ruta, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Buscar el sidebar
        match = PATRON_SIDEBAR.search(contenido)
        if not match:
            return False, "No se encontró sidebar"
        
        # Verificar si ya tiene el include
        if "{% include '_sidebar.html' %}" in contenido:
            return False, "Ya está actualizado"
        
        # Reemplazar el sidebar por el include
        nuevo_contenido = PATRON_SIDEBAR.sub(REEMPLAZO, contenido, count=1)
        
        # Guardar
        with open(ruta, 'w', encoding='utf-8') as f:
            f.write(nuevo_contenido)
        
        return True, "✅ Actualizado"
    except Exception as e:
        return False, f"❌ Error: {str(e)}"

def main():
    print("=" * 60)
    print("  ACTUALIZADOR DE SIDEBARS - Pagadiario")
    print("=" * 60)
    print(f"  Carpeta: {TEMPLATES_DIR}")
    print("=" * 60)
    
    if not os.path.exists(TEMPLATES_DIR):
        print(f"❌ No existe la carpeta: {TEMPLATES_DIR}")
        return
    
    archivos = [f for f in os.listdir(TEMPLATES_DIR) if f.endswith('.html')]
    print(f"\n📁 Archivos encontrados: {len(archivos)}\n")
    
    actualizados = 0
    omitidos = 0
    errores = 0
    
    for archivo in sorted(archivos):
        # Saltar los que no deben modificarse
        if archivo in ['_sidebar.html', 'base.html', 'login.html', 'dashboard.html']:
            print(f"⏭️  {archivo}: Omitido (especial)")
            omitidos += 1
            continue
        
        ruta = os.path.join(TEMPLATES_DIR, archivo)
        exito, mensaje = procesar_archivo(ruta)
        
        if exito:
            print(f"{mensaje}  {archivo}")
            actualizados += 1
        else:
            print(f"⏭️  {archivo}: {mensaje}")
            omitidos += 1
    
    print("\n" + "=" * 60)
    print(f"  ✅ Actualizados: {actualizados}")
    print(f"  ⏭️  Omitidos:    {omitidos}")
    print(f"  ❌ Errores:      {errores}")
    print("=" * 60)
    print("\n¡Listo! Reinicia Flask para ver los cambios.\n")

if __name__ == '__main__':
    main()