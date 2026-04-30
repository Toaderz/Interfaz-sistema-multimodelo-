#!/usr/bin/env python3
"""
RESEARCH WORKER v2.0 - API Ollama Cloud
========================================
Este worker se ejecuta ANTES del CEO Orchestrator.
Usa la API de Ollama en la nube (no CLI local) para acceder a modelos
potentes usando la API key configurada en OpenClaw.

Ventajas:
- No requiere descargar modelos localmente
- Usa la API key ya configurada
- Accede a modelos más potentes en la nube
"""

import os
import requests
import json
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path


# Cargar configuracion desde openclaw.json
OPENCLAW_CONFIG = Path.home() / ".openclaw" / "openclaw.json"

def load_ollama_config():
    """Carga configuracion de Ollama desde openclaw.json."""
    try:
        with open(OPENCLAW_CONFIG, 'r') as f:
            config = json.load(f)
        
        # Buscar API key de Ollama
        ollama_config = config.get("models", {}).get("providers", {}).get("ollama", {})
        api_key = ollama_config.get("apiKey", "")
        base_url = ollama_config.get("baseUrl", "https://ollama.com")
        
        return api_key, base_url
    except Exception as e:
        print(f"Warning: No se pudo cargar config: {e}")
        return "", "https://ollama.com"

OLLAMA_API_KEY, OLLAMA_BASE_URL = load_ollama_config()

# Modelos disponibles en Ollama Cloud
MODELOS = {
    "research": "kimi-k2.5:cloud",
    "analysis": "glm-5.1:cloud",
    "coding": "qwen3-coder-next:cloud"
}


@dataclass
class ResearchResult:
    """Resultado de la investigacion del Research Worker."""
    original_task: str = ""
    system_context: Dict[str, Any] = field(default_factory=dict)
    gaps: List[str] = field(default_factory=list)
    best_practices: List[str] = field(default_factory=list)
    top_repositories: List[Dict] = field(default_factory=list)
    optimized_prompt: str = ""
    estimated_tokens: int = 0
    confidence: float = 0.0


class ResearchWorker:
    """
    Research Worker usando API Ollama Cloud.
    Permite usar modelos potentes sin descargarlos localmente.
    """
    
    def __init__(self):
        self.name = "ResearchWorker"
        self.model = MODELOS["research"]
        self.api_key = OLLAMA_API_KEY
        self.base_url = OLLAMA_BASE_URL
        
        if not self.api_key:
            print("Warning: No se encontro API key de Ollama")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
    def _call_ollama_api(self, prompt: str, model: str = None) -> str:
        """Llama a la API de Ollama Cloud."""
        model = model or self.model
        
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                headers=self.headers,
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "Eres un experto en investigacion de software y arquitectura de sistemas."},
                        {"role": "user", "content": prompt}
                    ],
                    "options": {
                        "temperature": 0.7
                    },
                    "stream": False
                },
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json()["message"]["content"]
            else:
                return f"Error API {response.status_code}: {response.text[:200]}"
                
        except Exception as e:
            return f"Error API Ollama: {e}"
    
    def investigate(self, task: str) -> ResearchResult:
        """Investiga la tarea completa via API."""
        print(f"\n[RESEARCH WORKER] Investigando con API Cloud ({self.model})...")
        
        # 1. Contexto actual
        context = self._analyze_system()
        
        # 2. Gaps via API
        gaps = self._identify_gaps(task, context)
        
        # 3. Best practices via API
        practices = self._research_best_practices(task)
        
        # 4. Prompt optimization via API
        optimized = self._optimize_prompt(task, context, gaps)
        
        return ResearchResult(
            original_task=task,
            system_context=context,
            gaps=gaps,
            best_practices=practices,
            optimized_prompt=optimized,
            estimated_tokens=len(optimized.split()),
            confidence=0.8 if gaps and practices else 0.5
        )
    
    def _analyze_system(self) -> Dict[str, Any]:
        """Analiza sistema actual."""
        return {
            "models": {
                "ceo": "claude-opus-4-7",
                "code_chief": "codex-2-20250506",
                "research": "kimi-k2.5:cloud",
                "validation": "glm-5.1:cloud",
                "coding_assistant": "qwen3-coder-next:cloud"
            },
            "skills": ["code-helper", "research-core", "web-scraping", "excel-automation"],
            "version": "4.0"
        }
    
    def _identify_gaps(self, task: str, context: Dict) -> List[str]:
        """Identifica gaps via API."""
        prompt = f"""Analiza esta tarea de desarrollo: "{task}"
        
        Sistema actual tiene skills: {', '.join(context['skills'])}
        
        Identifica que funcionalidades faltan o mejoras necesarias.
        Responde SOLO con una lista numerada."""
        
        response = self._call_ollama_api(prompt, MODELOS["analysis"])
        return [line.strip('- ') for line in response.split('\n') if line.strip() and (line[0].isdigit() or line.startswith('-'))]
    
    def _research_best_practices(self, task: str) -> List[str]:
        """Busca mejores practicas via API."""
        prompt = f"""Para la tarea: "{task}"
        
        Cual son las 5 mejores practicas de implementacion?
        Incluye: patrones de diseno, estrategias, consideraciones de rendimiento.
        Responde en lista numerada."""
        
        response = self._call_ollama_api(prompt, MODELOS["research"])
        return [line.strip() for line in response.split('\n') if line.strip() and any(c.isdigit() for c in line[:3])]
    
    def _optimize_prompt(self, task: str, context: Dict, gaps: List[str]) -> str:
        """Optimiza prompt via API."""
        prompt = f"""Optimiza este prompt para Claude Code:
        
        TAREA: {task}
        
        GAPS IDENTIFICADOS:
        {chr(10).join(f"- {gap}" for gap in gaps[:3])}
        
        REQUISITOS:
        1. Reduce tokens innecesarios
        2. Estructura clara con markdown
        3. Solo contexto RELEVANTE
        4. Instrucciones especificas y concisas
        5. Formato de salida explicito
        
        Genera el prompt optimizado:"""
        
        return self._call_ollama_api(prompt, MODELOS["coding"])
    
    def generate_enriched_task(self, research: ResearchResult) -> str:
        """Genera tarea enriquecida para CEO."""
        return f"""# TAREA ENRIQUECIDA

## Tarea Original
{research.original_task}

## Contexto del Sistema
- Skills: {', '.join(research.system_context.get('skills', []))}
- Modelos: {', '.join(research.system_context.get('models', {}).keys())}

## Gaps Identificados
{chr(10).join(f"{i+1}. {gap}" for i, gap in enumerate(research.gaps))}

## Mejores Practicas
{chr(10).join(f"- {bp}" for bp in research.best_practices[:5])}

## Prompt Optimizado
```
{research.optimized_prompt[:500]}...
```

## Tokens: {research.estimated_tokens} | Confianza: {research.confidence*100:.0f}%
"""


def run_research(task: str) -> Dict[str, Any]:
    """Ejecuta investigacion completa."""
    worker = ResearchWorker()
    result = worker.investigate(task)
    enriched = worker.generate_enriched_task(result)
    
    return {
        "original_task": task,
        "enriched_task": enriched,
        "gaps_count": len(result.gaps),
        "best_practices_count": len(result.best_practices),
        "confidence": result.confidence,
        "status": "COMPLETED"
    }


if __name__ == "__main__":
    print("="*70)
    print("RESEARCH WORKER v2.0 - API Ollama Cloud")
    print("="*70)
    
    task = "Implementar sistema multi-agente con wake-up mechanism"
    result = run_research(task)
    
    print(f"\nResultado:")
    print(f"  Gaps: {result['gaps_count']}")
    print(f"  Best practices: {result['best_practices_count']}")
    print(f"  Confianza: {result['confidence']*100:.0f}%")
    print(f"\nTarea enriquecida lista para CEO!")
