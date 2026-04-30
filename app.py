#!/usr/bin/env python3
"""
Dashboard Web para Sistema Multiagente v4.0
Con login, control del sistema, aprobacion de planes e integracion real
"""

import os
import sys
import json
import threading
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from functools import wraps

# Importar integracion con sistema multiagente
from integracion_multiagente import integracion

app = Flask(__name__)
app.secret_key = 'sistema-multiagente-secreto-2024'

# Configuracion de login
USUARIO = "Toaderz"
CONTRASENA = "Doky2010"

# Estado sincronizado con integracion
estado_sistema = integracion.estado

# Plan pendiente de aprobacion
plan_pendiente = {
    'tarea': '',
    'plan': None,
    'status': 'NONE'  # NONE, ESPERANDO, APROBADO, RECHAZADO
}

def requiere_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logueado' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def raiz():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        contrasena = request.form.get('contrasena')
        
        if usuario == USUARIO and contrasena == CONTRASENA:
            session['logueado'] = True
            session['usuario'] = usuario
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Credenciales incorrectas")
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
@requiere_login
def dashboard():
    return render_template('dashboard.html', estado=estado_sistema, plan=plan_pendiente)

@app.route('/api/estado')
@requiere_login
def api_estado():
    return jsonify({
        **estado_sistema,
        'plan_pendiente': plan_pendiente
    })

@app.route('/api/generar_plan', methods=['POST'])
@requiere_login
def api_generar_plan():
    """Generar plan para aprobacion del usuario"""
    global plan_pendiente
    
    tarea = request.json.get('tarea', '')
    
    if not tarea:
        return jsonify({"error": "Tarea requerida"}), 400
    
    # Generar plan usando el sistema multiagente
    try:
        from integracion_multiagente import integracion
        
        # Generar plan (sin ejecutar)
        plan = integracion.generar_plan(tarea)
        
        plan_pendiente = {
            'tarea': tarea,
            'plan': plan,
            'status': 'ESPERANDO'
        }
        
        estado_sistema['status'] = 'ESPERANDO_APROBACION'
        estado_sistema['fase'] = 'Plan generado, esperando aprobacion'
        
        return jsonify({
            "status": "PLAN_GENERADO",
            "plan": plan,
            "mensaje": "Plan generado. Por favor revisa y aprueba o rechaza."
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/aprobar_plan', methods=['POST'])
@requiere_login
def api_aprobar_plan():
    """Aprobar plan y ejecutar tarea"""
    global plan_pendiente
    
    if plan_pendiente['status'] != 'ESPERANDO':
        return jsonify({"error": "No hay plan pendiente de aprobacion"}), 400
    
    tarea = plan_pendiente['tarea']
    
    # Marcar como aprobado
    plan_pendiente['status'] = 'APROBADO'
    
    # Reiniciar estado
    estado_sistema['status'] = 'RUNNING'
    estado_sistema['tarea_actual'] = tarea
    estado_sistema['fase'] = 'Ejecutando tarea aprobada...'
    estado_sistema['agentes_activos'] = []
    estado_sistema['logs'] = [f"[{datetime.now().strftime('%H:%M:%S')}] Plan aprobado. Iniciando tarea: {tarea}"]
    
    # Ejecutar en background
    integracion.ejecutar_en_background(tarea)
    
    return jsonify({
        "status": "EJECUTANDO",
        "tarea": tarea,
        "mensaje": "Plan aprobado. Ejecutando tarea..."
    })

@app.route('/api/rechazar_plan', methods=['POST'])
@requiere_login
def api_rechazar_plan():
    """Rechazar plan"""
    global plan_pendiente
    
    if plan_pendiente['status'] != 'ESPERANDO':
        return jsonify({"error": "No hay plan pendiente de aprobacion"}), 400
    
    plan_pendiente['status'] = 'RECHAZADO'
    estado_sistema['status'] = 'IDLE'
    estado_sistema['fase'] = 'Plan rechazado por usuario'
    
    return jsonify({
        "status": "RECHAZADO",
        "mensaje": "Plan rechazado. Puedes enviar una nueva tarea."
    })

@app.route('/api/ejecutar', methods=['POST'])
@requiere_login
def api_ejecutar():
    """Ejecutar tarea directamente (sin aprobacion)"""
    tarea = request.json.get('tarea', '')
    
    if not tarea:
        return jsonify({"error": "Tarea requerida"}), 400
    
    # Reiniciar estado
    estado_sistema['status'] = 'RUNNING'
    estado_sistema['tarea_actual'] = tarea
    estado_sistema['fase'] = 'Iniciando...'
    estado_sistema['agentes_activos'] = []
    estado_sistema['logs'] = [f"[{datetime.now().strftime('%H:%M:%S')}] Iniciando tarea: {tarea}"]
    
    # Ejecutar en background
    integracion.ejecutar_en_background(tarea)
    
    return jsonify({
        "status": "STARTED",
        "tarea": tarea,
        "mensaje": "Tarea iniciada correctamente. El sistema multiagente esta procesando..."
    })

@app.route('/api/metricas')
@requiere_login
def api_metricas():
    """API para obtener metricas de tokens por modelo"""
    metricas = integracion.metrics
    
    # Calcular totales
    total_tokens = sum(m['tokens'] for m in metricas.values())
    total_costo = sum(m['costo'] for m in metricas.values())
    total_tareas = sum(m['tareas'] for m in metricas.values())
    
    return jsonify({
        "metricas_por_modelo": metricas,
        "totales": {
            "tokens_usados": total_tokens,
            "costo_estimado_usd": round(total_costo, 4),
            "tareas_completadas": total_tareas
        }
    })

@app.route('/metricas')
@requiere_login
def metricas_page():
    """Pagina de metricas detalladas"""
    return render_template('metricas.html')

@app.route('/api/detener', methods=['POST'])
@requiere_login
def api_detener():
    """API para detener el sistema"""
    estado_sistema['status'] = 'STOPPED'
    estado_sistema['fase'] = 'DETENIDO POR USUARIO'
    estado_sistema['agentes_activos'] = []
    estado_sistema['logs'].append(f"[{datetime.now().strftime('%H:%M:%S')}] Sistema detenido por {session.get('usuario', 'unknown')}")
    return jsonify({"status": "STOPPED", "mensaje": "Sistema detenido"})

import os
PORT = int(os.environ.get('PORT', 5000))

if __name__ == '__main__':
    print("="*70)
    print("DASHBOARD MULTIAGENTE v4.0")
    print("="*70)
    print(f"URL: http://localhost:{PORT}")
    print(f"Usuario: {USUARIO}")
    print(f"Contrasena: {CONTRASENA}")
    print("="*70)
    app.run(host='0.0.0.0', port=PORT, debug=False)
