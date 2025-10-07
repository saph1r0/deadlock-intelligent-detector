"""
Motor de Detección de Deadlocks con RAG (Resource Allocation Graph)
FASE 3-4: Análisis Multi-Nivel y Construcción de Grafo
"""

import json
from typing import List, Dict, Set, Tuple
from collections import defaultdict
from dataclasses import dataclass


@dataclass
class DeadlockReport:
    """Reporte de deadlock detectado"""
    threads_involved: List[str]
    resources_involved: List[str]
    cycle_path: List[str]
    probability: float
    severity: str  # 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    analysis_level: int
    line_numbers: List[int]


class ResourceAllocationGraph:
    """Grafo de Asignación de Recursos (RAG) para detección de deadlocks"""
    
    def __init__(self):
        # Grafo dirigido: nodo -> [nodos destino]
        self.graph: Dict[str, Set[str]] = defaultdict(set)
        # Tipo de nodo: 'thread' o 'resource'
        self.node_types: Dict[str, str] = {}
        # Aristas únicas (desde, hacia, tipo)
        self.edges: Set[Tuple[str, str, str]] = set()
        
    def add_thread(self, thread_name: str):
        self.node_types[thread_name] = 'thread'
        self.graph.setdefault(thread_name, set())
        
    def add_resource(self, resource_name: str):
        self.node_types[resource_name] = 'resource'
        self.graph.setdefault(resource_name, set())
        
    def add_hold_edge(self, thread: str, resource: str):
        """Thread POSEE un recurso (thread → resource)"""
        if resource not in self.graph[thread]:
            self.graph[thread].add(resource)
            self.edges.add((thread, resource, 'hold'))
        
    def add_request_edge(self, resource: str, thread: str):
        """Thread ESPERA un recurso (resource → thread)"""
        if thread not in self.graph[resource]:
            self.graph[resource].add(thread)
            self.edges.add((resource, thread, 'request'))
        
    def detect_cycles(self) -> List[List[str]]:
        """Detecta ciclos en el grafo usando DFS"""
        visited = set()
        rec_stack = []
        cycles = []

        def dfs(node):
            if node in rec_stack:
                idx = rec_stack.index(node)
                cycle = rec_stack[idx:] + [node]
                cycles.append(cycle)
                return
            if node in visited:
                return
            visited.add(node)
            rec_stack.append(node)
            for nbr in self.graph.get(node, []):
                dfs(nbr)
            rec_stack.pop()

        for node in list(self.graph.keys()):
            if node not in visited:
                dfs(node)

        # Normalizar ciclos para evitar duplicados rotacionales
        normalized = []
        seen_signatures = set()
        for c in cycles:
            cyclic = c[:-1] if len(c) > 1 and c[0] == c[-1] else c
            if not cyclic:
                continue
            min_rot = min(tuple(cyclic[i:] + cyclic[:i]) for i in range(len(cyclic)))
            if min_rot not in seen_signatures:
                seen_signatures.add(min_rot)
                normalized.append(list(min_rot))
        return normalized
    
    def visualize_ascii(self) -> str:
        """Genera visualización ASCII del grafo (sin duplicados)"""
        lines = ["", "📊 RESOURCE ALLOCATION GRAPH:", ""]
        
        lines.append("🔵 THREADS:")
        for node, ntype in self.node_types.items():
            if ntype == 'thread':
                neighbors = sorted(self.graph.get(node, []))
                lines.append(f"   {node} → [{', '.join(neighbors)}]" if neighbors else f"   {node}")
        
        lines.append("")
        lines.append("🔒 RESOURCES:")
        for node, ntype in self.node_types.items():
            if ntype == 'resource':
                waiting = sorted(self.graph.get(node, []))
                lines.append(f"   {node} → [{', '.join(waiting)}]" if waiting else f"   {node}")
        
        lines.append("")
        lines.append("🔁 EDGES:")
        for a, b, etype in sorted(self.edges):
            lines.append(f"   {a} -[{etype}]-> {b}")
        
        return "\n".join(lines)


class MultiLevelDeadlockDetector:
    """Detector Multi-Nivel de Deadlocks"""
    
    def __init__(self):
        self.rag = ResourceAllocationGraph()
        self.operations: List[Dict] = []
        self.analysis_data: Dict = {}
        
    def load_analysis(self, json_path: str):
        with open(json_path, 'r', encoding='utf-8') as f:
            self.analysis_data = json.load(f)
        self.operations = self.analysis_data.get('operations', [])
        
    def build_rag(self):
        """Construye el RAG a partir de las operaciones detectadas"""
        threads = {op['thread'] for op in self.operations}
        resources = {op['resource'] for op in self.operations}
        
        for t in threads:
            self.rag.add_thread(t)
        for r in resources:
            self.rag.add_resource(r)
        
        owners: Dict[str, Set[str]] = defaultdict(set)
        
        for op in sorted(self.operations, key=lambda o: o.get('line', 0)):
            t, r, a = op['thread'], op['resource'], op['action']
            if a == 'acquire':
                other_owners = owners.get(r, set()) - {t}
                if other_owners:
                    self.rag.add_request_edge(r, t)
                owners[r].add(t)
                self.rag.add_hold_edge(t, r)
            elif a == 'release' and t in owners.get(r, set()):
                owners[r].remove(t)
    
    def level1_static_analysis(self) -> List[DeadlockReport]:
        cycles = self.rag.detect_cycles()
        reports = []
        for c in cycles:
            threads = [n for n in c if self.rag.node_types.get(n) == 'thread']
            resources = [n for n in c if self.rag.node_types.get(n) == 'resource']
            if len(threads) >= 2 and len(resources) >= 1:
                lines = [
                    op['line'] for op in self.operations
                    if op.get('thread') in threads and op.get('resource') in resources
                    and op.get('action') == 'acquire'
                ]
                reports.append(DeadlockReport(
                    threads_involved=threads,
                    resources_involved=resources,
                    cycle_path=c,
                    probability=0.85,
                    severity='HIGH',
                    analysis_level=1,
                    line_numbers=sorted(set(lines))
                ))
        return reports
    
    def level2_control_flow_analysis(self) -> List[DeadlockReport]:
        reports = []
        thread_ops = defaultdict(list)
        for op in sorted(self.operations, key=lambda o: o.get('line', 0)):
            if op['action'] == 'acquire':
                thread_ops[op['thread']].append(op)
        
        threads = list(thread_ops.keys())
        for i, t1 in enumerate(threads):
            for t2 in threads[i + 1:]:
                ops1, ops2 = thread_ops[t1], thread_ops[t2]
                if len(ops1) >= 2 and len(ops2) >= 2:
                    r1 = [o['resource'] for o in ops1[:2]]
                    r2 = [o['resource'] for o in ops2[:2]]
                    if set(r1) == set(r2) and r1 != r2 and r1 == list(reversed(r2)):
                        reports.append(DeadlockReport(
                            threads_involved=[t1, t2],
                            resources_involved=r1,
                            cycle_path=[t1, r1[0], t2, r1[1], t1],
                            probability=0.65,
                            severity='MEDIUM',
                            analysis_level=2,
                            line_numbers=[ops1[0].get('line', 0), ops2[0].get('line', 0)]
                        ))
        return reports
    
    def analyze(self) -> Dict:
        self.build_rag()
        reports = self.level1_static_analysis() + self.level2_control_flow_analysis()
        return {
            "total_deadlocks_detected": len(reports),
            "by_severity": {
                "CRITICAL": sum(r.severity == "CRITICAL" for r in reports),
                "HIGH": sum(r.severity == "HIGH" for r in reports),
                "MEDIUM": sum(r.severity == "MEDIUM" for r in reports),
                "LOW": sum(r.severity == "LOW" for r in reports)
            },
            "deadlocks": [r.__dict__ for r in reports],
            "rag_visualization": self.rag.visualize_ascii()
        }
    
    def export_report(self, output_path: str):
        report = self.analyze()
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        print("\n✓ Reporte de deadlocks exportado a:", output_path)
        print(report['rag_visualization'])
        if report['total_deadlocks_detected']:
            print(f"\n⚠️  DEADLOCKS DETECTADOS: {report['total_deadlocks_detected']}")
            for s, c in report['by_severity'].items():
                if c:
                    print(f"   {s}: {c}")
        else:
            print("\n✓ No se detectaron deadlocks")


if __name__ == "__main__":
    detector = MultiLevelDeadlockDetector()
    detector.load_analysis("reports/analysis_output.json")
    detector.export_report("reports/deadlock_report.json")
