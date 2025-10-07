"""
Base de Conocimiento y Sistema de Aprendizaje Incremental
FASE 7: Registro de patrones y soluciones efectivas
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class PatternRecord:
    """Registro de un patrón de deadlock detectado"""
    pattern_id: str
    pattern_name: str
    detected_in_file: str
    detection_date: str
    threads_involved: List[str]
    resources_involved: List[str]
    solution_applied: Optional[str] = None
    solution_effective: Optional[bool] = None
    user_feedback: Optional[int] = None  # 1-5 rating
    notes: str = ""


@dataclass
class SolutionRecord:
    """Registro de una solución aplicada"""
    solution_id: str
    solution_name: str
    times_used: int
    times_successful: int
    avg_user_rating: float
    complexity: str
    performance_impact: str


class KnowledgeBase:
    """Sistema de base de conocimiento con aprendizaje incremental"""
    
    def __init__(self, db_path: str = "data/knowledge_base.json"):
        self.db_path = Path(db_path)
        self.patterns: Dict[str, PatternRecord] = {}
        self.solutions: Dict[str, SolutionRecord] = {}
        self.history: List[Dict] = []
        
        self._load_database()
    
    def _load_database(self):
        """Carga la base de conocimiento desde JSON"""
        if self.db_path.exists():
            with open(self.db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Cargar patrones
                for p_data in data.get('patterns', []):
                    pattern = PatternRecord(**p_data)
                    self.patterns[pattern.pattern_id] = pattern
                
                # Cargar soluciones
                for s_data in data.get('solutions', []):
                    solution = SolutionRecord(**s_data)
                    self.solutions[solution.solution_id] = solution
                
                # Cargar historial
                self.history = data.get('history', [])
        else:
            # Crear base de datos inicial con patrones conocidos
            self._initialize_default_patterns()
    
    def _initialize_default_patterns(self):
        """Inicializa patrones por defecto basados en la literatura"""
        default_patterns = [
            {
                "pattern_id": "classic_two_thread",
                "pattern_name": "Classic Two-Thread Deadlock",
                "detected_in_file": "",
                "detection_date": "",
                "threads_involved": [],
                "resources_involved": [],
                "solution_applied": None,
                "solution_effective": None,
                "user_feedback": None,
                "notes": "Patrón clásico: 2 threads, 2 locks, orden inverso"
            },
            {
                "pattern_id": "nested_locks_3_levels",
                "pattern_name": "Nested Lock Acquisition (3+ levels)",
                "detected_in_file": "",
                "detection_date": "",
                "threads_involved": [],
                "resources_involved": [],
                "solution_applied": None,
                "solution_effective": None,
                "user_feedback": None,
                "notes": "Adquisición anidada profunda de locks"
            },
            {
                "pattern_id": "dining_philosophers",
                "pattern_name": "Dining Philosophers Variant",
                "detected_in_file": "",
                "detection_date": "",
                "threads_involved": [],
                "resources_involved": [],
                "solution_applied": None,
                "solution_effective": None,
                "user_feedback": None,
                "notes": "Patrón circular de recursos"
            }
        ]
        
        # Soluciones conocidas
        default_solutions = [
            {
                "solution_id": "lock_ordering",
                "solution_name": "Lock Ordering Strategy",
                "times_used": 0,
                "times_successful": 0,
                "avg_user_rating": 0.0,
                "complexity": "LOW",
                "performance_impact": "NONE"
            },
            {
                "solution_id": "try_lock_timeout",
                "solution_name": "Try-Lock with Timeout",
                "times_used": 0,
                "times_successful": 0,
                "avg_user_rating": 0.0,
                "complexity": "MEDIUM",
                "performance_impact": "LOW"
            },
            {
                "solution_id": "lock_hierarchy",
                "solution_name": "Lock Hierarchy",
                "times_used": 0,
                "times_successful": 0,
                "avg_user_rating": 0.0,
                "complexity": "HIGH",
                "performance_impact": "NONE"
            }
        ]
        
        for p in default_patterns:
            pattern = PatternRecord(**p)
            self.patterns[pattern.pattern_id] = pattern
        
        for s in default_solutions:
            solution = SolutionRecord(**s)
            self.solutions[solution.solution_id] = solution
        
        self._save_database()
    
    def _save_database(self):
        """Guarda la base de conocimiento a JSON"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "patterns": [asdict(p) for p in self.patterns.values()],
            "solutions": [asdict(s) for s in self.solutions.values()],
            "history": self.history,
            "last_updated": datetime.now().isoformat()
        }
        
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def register_detection(self, pattern_id: str, filename: str, 
                          threads: List[str], resources: List[str],
                          notes: str = "") -> bool:
        """Registra una nueva detección de patrón"""
        if pattern_id not in self.patterns:
            # Crear nuevo patrón
            pattern = PatternRecord(
                pattern_id=pattern_id,
                pattern_name=f"Pattern {pattern_id}",
                detected_in_file=filename,
                detection_date=datetime.now().isoformat(),
                threads_involved=threads,
                resources_involved=resources,
                notes=notes
            )
            self.patterns[pattern_id] = pattern
        else:
            # Actualizar patrón existente
            pattern = self.patterns[pattern_id]
            pattern.detected_in_file = filename
            pattern.detection_date = datetime.now().isoformat()
            pattern.threads_involved = threads
            pattern.resources_involved = resources
        
        # Añadir al historial
        self.history.append({
            "event": "detection",
            "pattern_id": pattern_id,
            "filename": filename,
            "timestamp": datetime.now().isoformat()
        })
        
        self._save_database()
        return True
    
    def register_solution_applied(self, pattern_id: str, solution_id: str,
                                 success: bool, user_rating: int = None) -> bool:
        """Registra que se aplicó una solución"""
        if pattern_id not in self.patterns:
            return False
        
        # Actualizar patrón
        pattern = self.patterns[pattern_id]
        pattern.solution_applied = solution_id
        pattern.solution_effective = success
        pattern.user_feedback = user_rating
        
        # Actualizar estadísticas de la solución
        if solution_id in self.solutions:
            solution = self.solutions[solution_id]
            solution.times_used += 1
            if success:
                solution.times_successful += 1
            
            if user_rating is not None:
                # Calcular nuevo promedio
                total_ratings = solution.times_used
                current_sum = solution.avg_user_rating * (total_ratings - 1)
                solution.avg_user_rating = (current_sum + user_rating) / total_ratings
        
        # Añadir al historial
        self.history.append({
            "event": "solution_applied",
            "pattern_id": pattern_id,
            "solution_id": solution_id,
            "success": success,
            "rating": user_rating,
            "timestamp": datetime.now().isoformat()
        })
        
        self._save_database()
        return True
    
    def get_recommended_solution(self, pattern_id: str) -> Optional[str]:
        """Obtiene la solución más recomendada para un patrón"""
        # Buscar en historial soluciones exitosas para este patrón
        pattern_history = [h for h in self.history 
                          if h.get('pattern_id') == pattern_id 
                          and h.get('event') == 'solution_applied'
                          and h.get('success') == True]
        
        if not pattern_history:
            # Si no hay historial, usar la solución con mejor rating general
            best_solution = max(
                self.solutions.values(),
                key=lambda s: (s.times_successful / max(s.times_used, 1), 
                             s.avg_user_rating),
                default=None
            )
            return best_solution.solution_id if best_solution else "lock_ordering"
        
        # Encontrar la solución más usada con éxito
        from collections import Counter
        solution_counts = Counter(h['solution_id'] for h in pattern_history)
        return solution_counts.most_common(1)[0][0]
    
    def get_pattern_statistics(self, pattern_id: str) -> Dict:
        """Obtiene estadísticas de un patrón"""
        if pattern_id not in self.patterns:
            return {}
        
        pattern = self.patterns[pattern_id]
        
        # Contar detecciones
        detections = len([h for h in self.history 
                         if h.get('pattern_id') == pattern_id 
                         and h.get('event') == 'detection'])
        
        # Contar soluciones aplicadas
        solutions_applied = len([h for h in self.history 
                                if h.get('pattern_id') == pattern_id 
                                and h.get('event') == 'solution_applied'])
        
        # Tasa de éxito
        successful = len([h for h in self.history 
                         if h.get('pattern_id') == pattern_id 
                         and h.get('event') == 'solution_applied'
                         and h.get('success') == True])
        
        success_rate = successful / solutions_applied if solutions_applied > 0 else 0.0
        
        return {
            "pattern_id": pattern_id,
            "pattern_name": pattern.pattern_name,
            "times_detected": detections,
            "solutions_attempted": solutions_applied,
            "success_rate": success_rate,
            "recommended_solution": self.get_recommended_solution(pattern_id),
            "last_seen": pattern.detection_date
        }
    
    def get_all_statistics(self) -> Dict:
        """Obtiene estadísticas generales de la base de conocimiento"""
        total_detections = len([h for h in self.history if h.get('event') == 'detection'])
        total_solutions = len([h for h in self.history if h.get('event') == 'solution_applied'])
        successful_solutions = len([h for h in self.history 
                                   if h.get('event') == 'solution_applied' 
                                   and h.get('success') == True])
        
        return {
            "total_patterns": len(self.patterns),
            "total_solutions": len(self.solutions),
            "total_detections": total_detections,
            "solutions_applied": total_solutions,
            "successful_solutions": successful_solutions,
            "success_rate": successful_solutions / total_solutions if total_solutions > 0 else 0.0,
            "most_detected_pattern": self._get_most_common_pattern(),
            "best_solution": self._get_best_solution()
        }
    
    def _get_most_common_pattern(self) -> str:
        """Obtiene el patrón más detectado"""
        from collections import Counter
        pattern_counts = Counter(h['pattern_id'] for h in self.history 
                               if h.get('event') == 'detection')
        if not pattern_counts:
            return "N/A"
        return pattern_counts.most_common(1)[0][0]
    
    def _get_best_solution(self) -> str:
        """Obtiene la solución con mejor desempeño"""
        if not self.solutions:
            return "N/A"
        
        best = max(
            self.solutions.values(),
            key=lambda s: (s.times_successful / max(s.times_used, 1), s.avg_user_rating)
        )
        return best.solution_name
    
    def print_statistics(self):
        """Imprime estadísticas formateadas"""
        stats = self.get_all_statistics()
        
        print("\n📚 ESTADÍSTICAS DE LA BASE DE CONOCIMIENTO\n")
        print(f"Total de patrones registrados: {stats['total_patterns']}")
        print(f"Total de soluciones disponibles: {stats['total_solutions']}")
        print(f"Detecciones totales: {stats['total_detections']}")
        print(f"Soluciones aplicadas: {stats['solutions_applied']}")
        print(f"Tasa de éxito: {stats['success_rate']*100:.1f}%")
        print(f"Patrón más común: {stats['most_detected_pattern']}")
        print(f"Mejor solución: {stats['best_solution']}")
        print()


# Ejemplo de uso
if __name__ == "__main__":
    kb = KnowledgeBase()
    
    # Ejemplo: Registrar una detección
    kb.register_detection(
        pattern_id="classic_two_thread",
        filename="examples/deadlock_example.py",
        threads=["thread_1", "thread_2"],
        resources=["lock_a", "lock_b"],
        notes="Deadlock clásico detectado"
    )
    
    # Aplicar solución
    kb.register_solution_applied(
        pattern_id="classic_two_thread",
        solution_id="lock_ordering",
        success=True,
        user_rating=5
    )
    
    # Obtener recomendación
    recommended = kb.get_recommended_solution("classic_two_thread")
    print(f"Solución recomendada: {recommended}")
    
    # Mostrar estadísticas
    kb.print_statistics()