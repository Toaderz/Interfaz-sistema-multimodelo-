#!/usr/bin/env python3
"""
Dashboard Web para Sistema Multiagente v4.0
Con login y control del sistema
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from functools import wraps

app = Flask(__name__)
app.secret_key = 'sistema-multiagente-secreto-2024'

# Configuración de login
USUARIO = "Toaderz"
CONTRASENA = "Doky2010"

# Datos de ejemplo del sistema
estado_sistema = {
    "status": "IDLE",
    "tarea_actual": "",
    "fase": "Esperando",
    "agentes_activos": [],
    "planes": [],
    "logs": []
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
    return render_template('dashboard.html', estado=estado_sistema)

@app.route('/api/estado')
@requiere_login
def api_estado():
    return jsonify(estado_sistema)

@app.route('/api/ejecutar', methods=['POST'])
@requiere_login
def api_ejecutar():
    tarea = request.json.get('tarea', '')
    
    if not tarea:
        return jsonify({"error": "Tarea requerida"}), 400
    
    # Actualizar estado
    estado_sistema['status'] = 'RUNNING'
    estado_sistema['tarea_actual'] = tarea
    estado_sistema['fase'] = 'Iniciando'
    estado_sistema['logs'].append(f"[{datetime.now().strftime('%H:%M:%S')}] Iniciando tarea: {tarea}")
    
    # Ejecutar sistema multiagente en segundo plano usando threading
    import threading
    def ejecutar_tarea_background(tarea_texto):
        try:
            estado_sistema['fase'] = 'Ollama Research investigando...'
            estado_sistema['agentes_activos'] = ['Ollama-Research']
            estado_sistema['logs'].append(f"[{datetime.now().strftime('%H:%M:%S')}] Ollama Research investigando gaps...")
            
            # Simular investigacion (aqui iria el codigo real)
            import time
            time.sleep(3)
            
            estado_sistema['fase'] = 'Claude CEO creando plan...'
            estado_sistema['agentes_activos'] = ['Claude-CEO']
            estado_sistema['logs'].append(f"[{datetime.now().strftime('%H:%M:%S')}] Claude CEO creando plan...")
            time.sleep(2)
            
            estado_sistema['fase'] = 'Ollama Coding generando codigo...'
            estado_sistema['agentes_activos'] = ['Ollama-Coding']
            estado_sistema['logs'].append(f"[{datetime.now().strftime('%H:%M:%S')}] Ollama Coding generando codigo...")
            time.sleep(4)
            
            estado_sistema['fase'] = 'Ollama Validation validando...'
            estado_sistema['agentes_activos'] = ['Ollama-Validation']
            estado_sistema['logs'].append(f"[{datetime.now().strftime('%H:%M:%S')}] Ollama Validation validando resultados...")
            time.sleep(2)
            
            estado_sistema['fase'] = 'Completado'
            estado_sistema['status'] = 'COMPLETED'
            estado_sistema['agentes_activos'] = []
            estado_sistema['planes'].append({
                "id": len(estado_sistema['planes']) + 1,
                "tarea": tarea_texto,
                "status": "COMPLETED",
                "fecha": datetime.now().isoformat()
            })
            estado_sistema['logs'].append(f"[{datetime.now().strftime('%H:%M:%S')}] Tarea completada exitosamente!")
            
        except Exception as e:
            estado_sistema['status'] = 'ERROR'
            estado_sistema['fase'] = f'Error: {str(e)}'
            estado_sistema['agentes_activos'] = []
            estado_sistema['logs'].append(f"[{datetime.now().strftime('%H:%M:%S')}] ERROR: {str(e)}")
    
    # Iniciar ejecucion en background
    thread = threading.Thread(target=ejecutar_tarea_background, args=(tarea,))
    thread.daemon = True
    thread.start()

@app.route('/api/aprobar_plan', methods=['POST'])
@requiere_login
def api_aprobar_plan():
    plan_id = request.json.get('plan_id')
    accion = request.json.get('accion')  # 'aprobar' o 'rechazar'
    
    for plan in estado_sistema['planes']:
        if plan['id'] == plan_id:
            plan['status'] = 'APPROVED' if accion == 'aprobar' else 'REJECTED'
            estado_sistema['logs'].append(
                f"[{datetime.now().strftime('%H:%M:%S')}] Plan {plan_id} {accion}ado por {session['usuario']}"
            )
            return jsonify({"status": "OK", "plan": plan})
    
    return jsonify({"error": "Plan no encontrado"}), 404

import os
PORT = int(os.environ.get('PORT', 5000))

if __name__ == '__main__':
    print("="*70)
    print("DASHBOARD MULTIAGENTE v4.0")
    print("="*70)
    print(f"URL: http://localhost:{PORT}")
    print(f"Usuario: {USUARIO}")
    print(f"Contraseña: {CONTRASENA}")
    print("="*70)
    app.run(host='0.0.0.0', port=PORT, debug=False)
