"""
Sistema de Recomendaciones Minimalista
FASE 6: Sugiere estrategias de corrección basadas en patterns.json
"""

import json
from pathlib import Path
from typing import List, Dict


class DeadlockRecommender:
    """Genera recomendaciones para deadlocks detectados"""
    
    def __init__(self, patterns_path: str = "data/patterns.json"):
        self.patterns = self._load_patterns(patterns_path)
        self.strategies = self.patterns.get("mitigation_strategies", [])
        
    def _load_patterns(self, path: str) -> Dict:
        """Carga base de conocimiento desde JSON"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️  Archivo {path} no encontrado. Usando estrategias por defecto.")
            return {"mitigation_strategies": []}
    
    def recommend(self, deadlock_report: Dict) -> List[Dict]:
        """Genera recomendaciones para un deadlock específico"""
        deadlocks = deadlock_report.get('deadlocks', [])
        
        if not deadlocks:
            return []
        
        recommendations = []
        
        for i, deadlock in enumerate(deadlocks, 1):
            severity = deadlock.get('severity', 'MEDIUM')
            num_threads = len(deadlock.get('threads', []))
            num_resources = len(deadlock.get('resources', []))
            
            # Scoring simple basado en efectividad y complejidad
            scored_strategies = []
            for strategy in self.strategies:
                score = self._calculate_score(strategy, severity, num_threads, num_resources)
                scored_strategies.append({
                    "strategy": strategy,
                    "score": score
                })
            
            # Ordenar por score descendente
            scored_strategies.sort(key=lambda x: x['score'], reverse=True)
            
            # Top 3 recomendaciones
            top_strategies = scored_strategies[:3]
            
            recommendations.append({
                "deadlock_id": i,
                "threads": deadlock.get('threads', []),
                "resources": deadlock.get('resources', []),
                "severity": severity,
                "probability": deadlock.get('probability', 0.0),
                "recommended_strategies": [
                    {
                        "name": s['strategy']['name'],
                        "id": s['strategy']['id'],
                        "score": s['score'],
                        "complexity": s['strategy']['complexity'],
                        "performance_impact": s['strategy']['performance_impact'],
                        "description": s['strategy']['description']
                    }
                    for s in top_strategies
                ]
            })
        
        return recommendations
    
    def _calculate_score(self, strategy: Dict, severity: str, num_threads: int, num_resources: int) -> float:
        """Calcula score de una estrategia (0-100)"""
        base_score = strategy.get('effectiveness', 50)
        
        # Ajustar por complejidad (preferir baja complejidad)
        complexity_penalty = {
            "LOW": 0,
            "MEDIUM": -5,
            "HIGH": -15
        }.get(strategy.get('complexity', 'MEDIUM'), -5)
        
        # Ajustar por impacto en performance (preferir bajo impacto)
        performance_penalty = {
            "NONE": 0,
            "LOW": -5,
            "MEDIUM": -10,
            "HIGH": -20,
            "POSITIVE": +10
        }.get(strategy.get('performance_impact', 'LOW'), -5)
        
        # Bonus por severidad alta (estrategias más efectivas)
        severity_bonus = {
            "CRITICAL": 10,
            "HIGH": 5,
            "MEDIUM": 0,
            "LOW": -5
        }.get(severity, 0)
        
        # Bonus por simplicidad en casos simples
        if num_threads == 2 and num_resources == 2:
            if strategy['id'] in ['lock_ordering', 'memory_address_ordering']:
                base_score += 10
        
        final_score = base_score + complexity_penalty + performance_penalty + severity_bonus
        return max(0, min(100, final_score))  # Clamp entre 0-100
    
    def generate_report(self, recommendations: List[Dict], output_path: str):
        """Genera reporte en Markdown"""
        lines = ["# 🔧 REPORTE DE RECOMENDACIONES\n"]
        
        for rec in recommendations:
            lines.append(f"## Deadlock #{rec['deadlock_id']}")
            lines.append(f"**Threads:** {', '.join(rec['threads'])}")
            lines.append(f"**Recursos:** {', '.join(rec['resources'])}")
            lines.append(f"**Severidad:** {rec['severity']}")
            lines.append(f"**Probabilidad:** {rec['probability']*100:.1f}%\n")
            
            lines.append("### 🎯 Estrategias Recomendadas:\n")
            
            for i, strategy in enumerate(rec['recommended_strategies'], 1):
                lines.append(f"#### {i}. {strategy['name']} (Score: {strategy['score']:.1f}/100)")
                lines.append(f"- **Complejidad:** {strategy['complexity']}")
                lines.append(f"- **Impacto en Performance:** {strategy['performance_impact']}")
                lines.append(f"- **Descripción:** {strategy['description']}\n")
            
            lines.append("---\n")
        
        # Escribir archivo
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print(f"✓ Recomendaciones exportadas a: {output_path}")
    
    def print_summary(self, recommendations: List[Dict]):
        """Imprime resumen en consola"""
        if not recommendations:
            print("\n✓ No hay recomendaciones que mostrar")
            return
        
        print("\n💡 RESUMEN DE RECOMENDACIONES:\n")
        
        for rec in recommendations:
            print(f"📌 Deadlock #{rec['deadlock_id']}:")
            print(f"   Threads: {', '.join(rec['threads'])}")
            print(f"   Recursos: {', '.join(rec['resources'])}")
            print(f"   Severidad: {rec['severity']}")
            print(f"   Probabilidad: {rec['probability']*100:.1f}%\n")
            
            print("   🔧 Top 3 Estrategias Recomendadas:")
            for i, strategy in enumerate(rec['recommended_strategies'], 1):
                print(f"      {i}. {strategy['name']} (Score: {strategy['score']:.1f}/100)")
                print(f"         • Complejidad: {strategy['complexity']}")
                print(f"         • Impacto: {strategy['performance_impact']}")
            print()


# Ejemplo de uso
if __name__ == "__main__":
    # Cargar reporte de deadlocks
    with open("reports/deadlock_report.json", 'r') as f:
        deadlock_report = json.load(f)
    
    # Generar recomendaciones
    recommender = DeadlockRecommender()
    recommendations = recommender.recommend(deadlock_report)
    
    # Mostrar en consola
    recommender.print_summary(recommendations)
    
    # Exportar a archivo
    recommender.generate_report(recommendations, "reports/recommendations.md")