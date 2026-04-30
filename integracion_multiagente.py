#!/usr/bin/env python3
"""
Integracion REAL entre Dashboard y Sistema Multiagente v4.0
SOLUCION TEMPORAL: Usa archivos locales hasta que se cree el repo Sistema-multiagentes
"""

import sys
import os
import json
import threading
import time
import subprocess
from datetime import datetime

# PATH LOCAL (solucion temporal hasta que exista el repo en GitHub)
MULTIAGENTE_PATH = os.path.dirname(os.path.abspath(__file__))
if MULTIAGENTE_PATH not in sys.path:
    sys.path.insert(0, MULTIAGENTE_PATH)

class IntegracionMultiagente:
    """Integracion que ejecuta el sistema multiagente real"""
    
    def __init__(self):
        self.metrics = {
            'claude': {'tokens': 0, 'costo': 0.0, 'tareas': 0},
            'ollama_research': {'tokens': 0, 'costo': 0.0, 'tareas': 0},
            'ollama_coding': {'tokens': 0, 'costo': 0.0, 'tareas': 0},
            'ollama_validation': {'tokens': 0, 'costo': 0.0, 'tareas': 0}
        }
        self.estado = {
            'status': 'IDLE',
            'fase': 'Esperando',
            'agentes_activos': [],
            'logs': []
        }
        self.resultado_final = None
    
    def ejecutar_tarea(self, tarea_texto):
        """Ejecutar tarea usando el sistema multiagente real"""
        try:
            self._log('Iniciando ejecucion con sistema multiagente v4.0...')
            
            # Importar el sistema multiagente real (archivos locales)
            from ceo_orchestrator_v4 import CEOOrchestratorV4
            
            # Crear instancia
            orchestrator = CEOOrchestratorV4()
            
            # Ejecutar tarea
            self._actualizar_estado('RUNNING', 'Ejecutando sistema multiagente...', ['Claude-CEO', 'Ollama-Research', 'Ollama-Coding', 'Ollama-Validation'])
            self._log('Ejecutando tarea con CEOOrchestratorV4...')
            
            resultado = orchestrator.execute_task(tarea_texto)
            
            # Procesar resultado
            if resultado.get('status') == 'COMPLETED':
                self._actualizar_estado('COMPLETED', 'Completado', [])
                self._log('Tarea completada exitosamente!')
                self._log(f"Modelos usados: {', '.join(resultado.get('models_used', []))}")
                self._log(f"CEO Action: {resultado.get('ceo_action', 'N/A')}")
                
                # Actualizar metricas
                models = resultado.get('models_used', [])
                if 'claude-opus-4-7' in models:
                    self._actualizar_metricas('claude', 200)
                if 'deepseek-v3.1:671b' in models:
                    self._actualizar_metricas('ollama_research', 500)
                if 'qwen3-coder-next' in models:
                    self._actualizar_metricas('ollama_coding', 1000)
                if 'gemma3:27b' in models:
                    self._actualizar_metricas('ollama_validation', 300)
                
                self.resultado_final = resultado
                return {
                    'status': 'COMPLETED',
                    'resultado': resultado,
                    'metricas': self.metrics
                }
            else:
                self._actualizar_estado('ERROR', f"Error: {resultado.get('error', 'Desconocido')}", [])
                self._log(f"Error en ejecucion: {resultado.get('error', 'Desconocido')}")
                return {
                    'status': 'ERROR',
                    'error': resultado.get('error', 'Error desconocido')
                }
            
        except Exception as e:
            self._actualizar_estado('ERROR', f'Error: {str(e)}', [])
            self._log(f'ERROR CRITICO: {str(e)}')
            import traceback
            self._log(traceback.format_exc())
            return {
                'status': 'ERROR',
                'error': str(e)
            }
    
    def ejecutar_en_background(self, tarea_texto):
        """Ejecutar tarea en un hilo separado"""
        thread = threading.Thread(target=self.ejecutar_tarea, args=(tarea_texto,))
        thread.daemon = True
        thread.start()
        return thread
    
    def _actualizar_estado(self, status, fase, agentes):
        self.estado['status'] = status
        self.estado['fase'] = fase
        self.estado['agentes_activos'] = agentes
    
    def _log(self, mensaje):
        hora = datetime.now().strftime('%H:%M:%S')
        log_entry = f'[{hora}] {mensaje}'
        self.estado['logs'].append(log_entry)
        if len(self.estado['logs']) > 100:
            self.estado['logs'] = self.estado['logs'][-100:]
    
    def _actualizar_metricas(self, agente, tokens):
        if agente in self.metrics:
            self.metrics[agente]['tokens'] += tokens
            precios = {
                'claude': 0.00015,
                'ollama_research': 0.00001,
                'ollama_coding': 0.00001,
                'ollama_validation': 0.00001
            }
            costo = (self.metrics[agente]['tokens'] / 1000) * precios.get(agente, 0.00001)
            self.metrics[agente]['costo'] = costo
            self.metrics[agente]['tareas'] += 1

# Instancia global
integracion = IntegracionMultiagente()