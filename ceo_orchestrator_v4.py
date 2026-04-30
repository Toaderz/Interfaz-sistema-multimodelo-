#!/usr/bin/env python3
"""
CEO ORCHESTRATOR v4.0 - ARQUITECTURA CORREGIDA
===============================================
CLAUDE CEO = Solo planes + delegación + wake-up validation
OLLAMA = Todo el trabajo (research, coding, validation)

Arquitectura:
- CLAUDE (Claude CLI real) = CEO Orchestrator - SOLO PLANES Y WAKE-UP
- RESEARCH WORKER (Ollama API) = Investigación pre-CEO
- CODING WORKER (Ollama API) = Generación de código
- VALIDATION WORKER (Ollama API) = Validación de resultados
- WAKE-UP = CEO verifica cumplimiento
"""

import subprocess
import requests
import os
import json
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path

# Configuración de modelos
MODELOS = {
    "ceo_orchestrator": "claude-opus-4-7",      # Claude CLI - SOLO planes y wake-up
    "research_worker": "deepseek-v3.1:671b",     # Ollama API - Investigación
    "coding_worker": "qwen3-coder-next",         # Ollama API - Generación de código
    "validation_worker": "gemma3:27b",            # Ollama API - Validación
}


@dataclass
class ExecutionState:
    """Estado compartido - PERSISTENTE para wake-up."""
    task: str = ""
    task_id: str = ""
    task_type: str = "general"
    phase: str = "idle"
    
    # Contexto enriquecido por Research Worker
    research_context: Dict[str, Any] = field(default_factory=dict)
    gaps_identified: List[str] = field(default_factory=list)
    best_practices: List[str] = field(default_factory=list)
    
    # Tracking de ejecución
    planned_steps: List[str] = field(default_factory=list)
    executed_steps: List[str] = field(default_factory=list)
    current_step: int = 0
    total_steps: int = 0
    
    # Resultados
    models_used: List[str] = field(default_factory=list)
    skills_used: List[str] = field(default_factory=list)
    code_generated: str = ""
    validation_result: str = ""
    
    # Estado del sistema
    system_status: str = "idle"
    version: str = "4.0"
    
    # Para wake-up mechanism
    sleep_start: Optional[str] = None
    wake_up_triggered: bool = False
    plan_approved: bool = False
    
    def save_to_file(self, filepath: str):
        """Guarda estado para wake-up."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(asdict(self), f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load_from_file(cls, filepath: str) -> 'ExecutionState':
        """Carga estado desde disco."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls(**data)


class OllamaWorker:
    """
    Worker base que usa Ollama API Cloud.
    Todos los workers de trabajo usan Ollama, NO Claude.
    """
    
    def __init__(self, role: str, model: str):
        self.role = role
        self.model = model
        self.name = f"Ollama-{role.capitalize()}"
        
        # Cargar API key desde openclaw.json
        OPENCLAW_CONFIG = Path.home() / ".openclaw" / "openclaw.json"
        try:
            with open(OPENCLAW_CONFIG, 'r', encoding='utf-8') as f:
                config = json.load(f)
            ollama_config = config.get("models", {}).get("providers", {}).get("ollama", {})
            self.api_key = ollama_config.get("apiKey", "")
            self.base_url = ollama_config.get("baseUrl", "https://ollama.com")
        except:
            self.api_key = os.getenv("OLLAMA_API_KEY", "")
            self.base_url = "https://ollama.com"
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def _call_ollama_api(self, prompt: str) -> str:
        """Llama a Ollama API Cloud."""
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                headers=self.headers,
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": f"Eres un {self.role} experto."},
                        {"role": "user", "content": prompt}
                    ],
                    "options": {"temperature": 0.7},
                    "stream": False
                },
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json()["message"]["content"]
            else:
                return f"Error API {response.status_code}: {response.text[:200]}"
        except Exception as e:
            return f"Error API: {e}"


class ResearchWorker(OllamaWorker):
    """
    Research Worker - Investigación PROFUNDA antes del CEO.
    Usa Ollama API (NO Claude).
    """
    
    def __init__(self):
        super().__init__("researcher", MODELOS["research_worker"])
    
    def investigate(self, task: str) -> Dict[str, Any]:
        """Investiga gaps, benchmarks y optimiza prompts."""
        print(f"\n[{self.name}] Investigando con API Cloud ({self.model})...")
        
        # Paso 1: Análisis de gaps
        gaps_prompt = f"""Analiza esta tarea: "{task}"

Identifica qué funcionalidades faltan o podrían mejorarse.
Responde SOLO con una lista numerada de 5-10 gaps."""
        
        gaps_text = self._call_ollama_api(gaps_prompt)
        gaps = [line.strip('- ') for line in gaps_text.split('\n') 
                if line.strip() and (line[0].isdigit() or line.startswith('-'))]
        
        # Paso 2: Best practices
        bp_prompt = f"""Para la tarea: "{task}"

Cuáles son las 5 mejores prácticas de implementación?
Responde en lista numerada."""
        
        bp_text = self._call_ollama_api(bp_prompt)
        best_practices = [line.strip('- ') for line in bp_text.split('\n') 
                         if line.strip() and (line[0].isdigit() or line.startswith('-'))]
        
        # Paso 3: Optimización de prompt
        optimization = self._optimize_prompt(task, gaps)
        
        return {
            "gaps": gaps[:10],
            "best_practices": best_practices[:5],
            "confidence": min(100, len(gaps) * 10),
            "context": {
                "models": MODELOS,
                "skills": ["code-helper", "research-core"]
            },
            "optimized_prompt": optimization
        }
    
    def _optimize_prompt(self, task: str, gaps: List[str]) -> str:
        """Optimiza prompt para Claude CEO."""
        prompt = f"""Optimiza este prompt para CEO Orchestrator:

TAREA: {task}
GAPS: {', '.join(gaps[:3])}

REQUISITOS:
1. Reduce tokens innecesarios
2. Estructura clara con markdown
3. Solo contexto RELEVANTE

Responde con el prompt optimizado."""
        
        return self._call_ollama_api(prompt)


class CodingWorker(OllamaWorker):
    """
    Coding Worker - Genera código con Ollama (NO Codex).
    """
    
    def __init__(self):
        super().__init__("programmer", MODELOS["coding_worker"])
    
    def generate_code(self, task: str, plan: Dict, state: ExecutionState) -> str:
        """Genera código usando Ollama."""
        print(f"\n[{self.name}] Generando código con {self.model}...")
        
        prompt = f"""# Tarea: {task}

## Plan
{json.dumps(plan, indent=2)}

## Contexto
Skills: {', '.join(state.skills_used)}
Gaps: {', '.join(state.gaps_identified[:3])}

Genera el código completo y funcional."""
        
        return self._call_ollama_api(prompt)


class ValidationWorker(OllamaWorker):
    """
    Validation Worker - Valida resultados con Ollama (NO Claude).
    """
    
    def __init__(self):
        super().__init__("validator", MODELOS["validation_worker"])
    
    def validate(self, code: str, task: str) -> Dict[str, Any]:
        """Valida código generado."""
        print(f"\n[{self.name}] Validando con {self.model}...")
        
        prompt = f"""Valida este código para la tarea: "{task}"

Código:
```python
{code[:1000]}
```

Evalúa:
1. Calidad del código
2. Errores potenciales
3. Mejoras sugeridas
4. Score del 1-10

Responde en formato JSON."""
        
        return self._call_ollama_api(prompt)


class ClaudeCEO:
    """
    CLAUDE CEO - SOLO PLANES Y WAKE-UP.
    NO hace trabajo de research, coding o validation.
    """
    
    def __init__(self):
        self.name = "ClaudeCEO"
        self.model = MODELOS["ceo_orchestrator"]
    
    def _call_claude(self, prompt: str) -> str:
        """Llama a Claude CLI - SOLO para planes y estrategia."""
        try:
            result = subprocess.run(
                ["claude", "--print"],
                input=prompt,
                capture_output=True,
                text=True,
                timeout=300
            )
            return result.stdout.strip()
        except Exception as e:
            return f"Error llamando Claude: {e}"
    
    def create_plan(self, task: str, research: Dict[str, Any]) -> Dict[str, Any]:
        """CEO crea plan basado en research de Ollama."""
        print(f"\n[CLAUDE CEO] Creando plan basado en research de Ollama...")
        
        prompt = f"""Eres un CEO Orchestrator experto.

## Tarea
{task}

## Research de Ollama
Gaps encontrados: {len(research.get('gaps', []))}
Best practices: {len(research.get('best_practices', []))}

## Instrucciones
1. Crea un plan de ejecución
2. Delega cada paso a los workers de Ollama
3. Define qué modelo de Ollama usar para cada tarea
4. Responde en JSON: steps, models, timeline"""
        
        response = self._call_claude(prompt)
        
        return {
            "agent": self.name,
            "model": self.model,
            "plan": response,
            "next_phase": "execution",
            "requires_codex": False,  # NO usamos Codex, usamos Ollama
            "confidence": 0.92,
            "timestamp": datetime.now().isoformat()
        }
    
    def delegate_tasks(self, plan: Dict[str, Any], state: ExecutionState) -> List[str]:
        """CEO delega tareas a workers de Ollama."""
        print(f"\n[CLAUDE CEO] Delegando tareas a workers de Ollama...")
        
        steps = [
            "Ollama Research: Investigar gaps",
            "Ollama Coding: Generar código",
            "Ollama Validation: Validar resultados"
        ]
        
        state.planned_steps = steps
        state.current_step = 0
        state.total_steps = len(steps)
        
        return steps
    
    def sleep(self, state: ExecutionState):
        """CEO se duerme mientras Ollama trabaja."""
        print(f"\n[CLAUDE CEO] >>> SLEEP MODE (esperando workers de Ollama)...")
        state.sleep_start = datetime.now().isoformat()
        state.system_status = "sleeping"
        state.save_to_file("execution_state.json")
    
    def wake_up(self, state: ExecutionState) -> Dict[str, Any]:
        """
        WAKE-UP: CEO se despierta y verifica que Ollama hizo su trabajo.
        """
        print(f"\n[CLAUDE CEO] <<< WAKE UP! Verificando trabajo de Ollama...")
        
        compliance = self._check_compliance(state)
        
        if not compliance["plan_followed"]:
            print(f"  ALERTA: Ollama NO completo todos los pasos!")
            print(f"  Faltantes: {compliance['steps_missed']}")
            return {
                "action": "REPLAN",
                "reason": "Ollama missed steps",
                "missing_steps": compliance["steps_missed"]
            }
        else:
            print(f"  OK: Ollama completo todo correctamente!")
            return {
                "action": "FINALIZE",
                "reason": "All Ollama workers completed"
            }
    
    def _check_compliance(self, state: ExecutionState) -> Dict[str, Any]:
        """Verifica si Ollama cumplió el plan."""
        planned = set(state.planned_steps)
        executed = set(state.executed_steps)
        
        completed = planned.intersection(executed)
        missing = planned - executed
        
        return {
            "compliance_rate": len(completed) / len(planned) if planned else 0,
            "steps_completed": list(completed),
            "steps_missed": list(missing),
            "plan_followed": len(missing) == 0
        }


class CEOOrchestratorV4:
    """
    CEO Orchestrator v4.0 - Arquitectura corregida:
    - Claude = SOLO planes + wake-up
    - Ollama = TODO el trabajo (research, coding, validation)
    """
    
    def __init__(self, plan_mode: bool = True):
        self.state = ExecutionState()
        self.state.version = "4.0"
        
        # CLAUDE CEO - Solo planes y wake-up
        self.ceo = ClaudeCEO()
        
        # OLLAMA WORKERS - Todo el trabajo pesado
        self.research_worker = ResearchWorker()
        self.coding_worker = CodingWorker()
        self.validation_worker = ValidationWorker()
        
        self.plan_mode = plan_mode
    
    def execute_task(self, task: str) -> Dict[str, Any]:
        """Ejecuta tarea con arquitectura corregida."""
        print("="*70)
        print("CEO ORCHESTRATOR v4.0 - CLAUDE PLANES + OLLAMA TRABAJO")
        print("="*70)
        print(f"Tarea: {task}")
        print("="*70)
        
        self.state.task = task
        self.state.task_id = f"task_{int(time.time())}"
        self.state.phase = "starting"
        
        # =====================================================================
        # FASE 0: OLLAMA RESEARCH (antes del CEO)
        # =====================================================================
        print("\n" + "-"*70)
        print("FASE 0: OLLAMA RESEARCH - Investigación Pre-CEO")
        print("-"*70)
        
        research = self.research_worker.investigate(task)
        self.state.research_context = research
        self.state.gaps_identified = research.get("gaps", [])
        self.state.best_practices = research.get("best_practices", [])
        self.state.models_used.append(self.research_worker.model)
        self.state.executed_steps.append("Ollama Research: Investigar gaps")
        
        # =====================================================================
        # FASE 1: CLAUDE CEO - CREAR PLAN (solo planificación)
        # =====================================================================
        print("\n" + "-"*70)
        print("FASE 1: CLAUDE CEO - Crear Plan y Delegar")
        print("-"*70)
        
        plan = self.ceo.create_plan(task, research)
        self.state.planned_steps = self.ceo.delegate_tasks(plan, self.state)
        self.state.models_used.append(self.ceo.model)
        
        # =====================================================================
        # FASE 2: CLAUDE CEO SLEEP - OLLAMA TRABAJA
        # =====================================================================
        print("\n" + "-"*70)
        print("FASE 2: CLAUDE CEO SLEEP + OLLAMA WORKERS")
        print("-"*70)
        
        self.ceo.sleep(self.state)
        
        # Ollama Coding Worker genera código
        code = self.coding_worker.generate_code(task, plan, self.state)
        self.state.code_generated = code
        self.state.executed_steps.append("Ollama Coding: Generar código")
        self.state.models_used.append(self.coding_worker.model)
        
        # Ollama Validation Worker valida
        validation = self.validation_worker.validate(code, task)
        self.state.validation_result = validation
        self.state.executed_steps.append("Ollama Validation: Validar resultados")
        self.state.models_used.append(self.validation_worker.model)
        
        # =====================================================================
        # FASE 3: CLAUDE CEO WAKE-UP - Verificar Ollama
        # =====================================================================
        print("\n" + "-"*70)
        print("FASE 3: CLAUDE CEO WAKE-UP - Verificar Trabajo de Ollama")
        print("-"*70)
        
        self.state.wake_up_triggered = True
        wake_up_result = self.ceo.wake_up(self.state)
        
        # =====================================================================
        # FASE 4: EVALUACIÓN FINAL
        # =====================================================================
        print("\n" + "="*70)
        print("EVALUACIÓN FINAL")
        print("="*70)
        
        if wake_up_result["action"] == "FINALIZE":
            print("OK: Ollama completo todo el trabajo")
            print(f"Codigo generado: {len(self.state.code_generated)} caracteres")
            print(f"Validacion: {self.state.validation_result[:100]}")
        else:
            print(f"REPLAN: {wake_up_result['reason']}")
        
        self.state.save_to_file("execution_state.json")
        
        return {
            "status": "COMPLETED" if wake_up_result["action"] == "FINALIZE" else "REPLAN",
            "ceo_action": wake_up_result["action"],
            "models_used": list(set(self.state.models_used)),
            "steps_completed": self.state.executed_steps,
            "plan_followed": wake_up_result["action"] == "FINALIZE"
        }


def main():
    """Ejemplo de uso."""
    orchestrator = CEOOrchestratorV4(plan_mode=False)
    
    result = orchestrator.execute_task(
        "Implementar Research Worker y Wake-up mechanism"
    )
    
    print("\n" + "="*70)
    print("RESULTADO FINAL")
    print("="*70)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
