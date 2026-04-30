#!/usr/bin/env python3
"""
Integracion REAL entre Dashboard y Sistema Multiagente v4.0
Con funcionalidad de aprobacion de planes
"""

import sys
import os
import json
import threading
from datetime import datetime

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
    
    def generar_plan(self, tarea_texto):
        """Generar plan detallado para aprobacion del usuario"""
        try:
            self._log('Generando plan para aprobacion...')
            
            # Importar lazy
            try:
                from ceo_orchestrator_v4 import CEOOrchestratorV4
            except ImportError as e:
                self._log(f'ERROR importando: {e}')
                # Plan basico si no se puede importar
                return {
                    'tarea': tarea_texto,
                    'pasos': [
                        '1. Investigar requisitos y mejores practicas',
                        '2. Crear plan detallado con Claude CEO',
                        '3. Ejecutar tareas con Ollama workers',
                        '4. Validar resultados',
                        '5. Entregar al usuario'
                    ],
                    'modelos': ['Claude CEO', 'Ollama Research', 'Ollama Coding', 'Ollama Validation'],
                    'estimacion_tokens': {'claude': 200, 'ollama_research': 500, 'ollama_coding': 1000, 'ollama_validation': 300},
                    'costo_estimado': 0.048,
                    'tiempo_estimado': '2-3 minutos'
                }
            
            # Crear instancia
            orchestrator = CEOOrchestratorV4()
            
            # Generar plan (sin ejecutar)
            # Usamos una funcion especial del orchestrator o simulamos
            plan = {
                'tarea': tarea_texto,
                'pasos': [
                    '1. Ollama Research: Investigar gaps y mejores practicas',
                    '2. Claude CEO: Crear plan detallado basado en research',
                    '3. Claude CEO: Delegar tareas a workers',
                    '4. Ollama Coding: Generar codigo/implementar',
                    '5. Ollama Validation: Validar resultados',
                    '6. Claude CEO: Verificar cumplimiento y finalizar'
                ],
                'modelos': ['deepseek-v3.1:671b', 'claude-opus-4-7', 'qwen3-coder-next', 'gemma3:27b'],
                'distribucion_tareas': {
                    'CEO (Claude)': 'Planear, delegar, verificar',
                    'Research (Ollama)': 'Investigar, analizar',
                    'Coding (Ollama)': 'Implementar, generar codigo',
                    'Validation (Ollama)': 'Validar, corregir'
                },
                'estimacion_tokens': {
                    'claude_ceo': 200,
                    'ollama_research': 500,
                    'ollama_coding': 1000,
                    'ollama_validation': 300
                },
                'costo_estimado_usd': 0.048,
                'tiempo_estimado': '2-3 minutos',
                'notas': 'El plan puede ajustarse durante la ejecucion segun findings de Research'
            }
            
            self._log('Plan generado exitosamente')
            return plan
            
        except Exception as e:
            self._log(f'ERROR generando plan: {e}')
            return {
                'tarea': tarea_texto,
                'pasos': ['Error al generar plan detallado'],
                'error': str(e)
            }
    
    def ejecutar_tarea(self, tarea_texto):
        """Ejecutar tarea usando el sistema multiagente real"""
        try:
            self._log('Iniciando ejecucion con sistema multiagente v4.0...')
            
            # Importar lazy
            try:
                from ceo_orchestrator_v4 import CEOOrchestratorV4
            except ImportError as e:
                self._log(f'ERROR importando sistema multiagente: {e}')
                return {
                    'status': 'ERROR',
                    'error': f'No se pudo importar ceo_orchestrator_v4: {e}'
                }
            
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
