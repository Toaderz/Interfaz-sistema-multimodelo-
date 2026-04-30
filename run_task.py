#!/usr/bin/env python3
"""Script para lanzar el sistema multiagentes con una tarea compleja."""

import sys
sys.path.insert(0, r'C:/Users/Alejandro Jimenez/.openclaw/workspace/Sistema-multiagentes')

from sistema_skills_inteligente import SistemaSkillsInteligente

# Leer la tarea del archivo
task_path = r'C:/Users/Alejandro Jimenez/.openclaw/workspace/Sistema-multiagentes/task_mejorar_sistema.md'
with open(task_path, 'r') as f:
    tarea = f.read()

print("="*70)
print("LANZANDO SISTEMA MULTIAGENTES v3.0")
print("="*70)
print(f"Tarea: Implementar Research Worker + Wake-up Mechanism")
print("="*70)

# Ejecutar con Plan Mode
sistema = SistemaSkillsInteligente(plan_mode=True)

# Simular aprobacion del usuario
import builtins
original_input = builtins.input
def mock_input(prompt=''):
    print(prompt + 's')
    return 's'
builtins.input = mock_input

try:
    resultado = sistema.ejecutar(tarea)
    print("\n" + "="*70)
    print("RESULTADO DEL SISTEMA")
    print("="*70)
    print(f"Status: {resultado['status']}")
    if resultado['status'] == 'COMPLETED':
        print(f"Score: {resultado['evaluation']['score_total']}/10")
        print("\nEl sistema ha completado la mejora automaticamente!")
    else:
        print(f"Resultado: {resultado.get('message', 'N/A')}")
finally:
    builtins.input = original_input
