"""
Analizador Sintáctico y Extractor de Locks
FASE 2: Detecta hilos y recursos (locks, mutexes, semáforos) en código fuente
"""

import ast
import json
from dataclasses import dataclass, asdict
from typing import List, Dict, Set
from pathlib import Path


@dataclass
class LockOperation:
    """Representa una operación sobre un lock"""
    thread: str
    resource: str
    action: str  # 'acquire' o 'release'
    line: int
    function: str


@dataclass
class ThreadInfo:
    """Información sobre un hilo detectado"""
    name: str
    created_at_line: int
    target_function: str
    locks_used: Set[str]


class CodeAnalyzer:
    """Analizador estático de código Python para detectar concurrencia"""
    
    def __init__(self):
        self.threads: Dict[str, ThreadInfo] = {}
        self.resources: Set[str] = set()
        self.operations: List[LockOperation] = []
        self.current_function = "main"
        
    def analyze_file(self, filepath: str) -> Dict:
        """Analiza un archivo Python y extrae información de concurrencia"""
        with open(filepath, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        tree = ast.parse(source_code, filename=filepath)
        self._analyze_tree(tree)
        
        return self._generate_report()
    
    def _analyze_tree(self, tree: ast.AST):
        """Recorre el AST buscando operaciones de threading y locks"""
        for node in ast.walk(tree):
            # Detectar definiciones de funciones
            if isinstance(node, ast.FunctionDef):
                self.current_function = node.name
            
            # Detectar creación de threads
            if isinstance(node, ast.Call):
                self._check_thread_creation(node)
                self._check_lock_operation(node)
            
            # Detectar declaración de locks
            if isinstance(node, ast.Assign):
                self._check_lock_declaration(node)
            self._check_with_statements(tree)
    
    def _check_thread_creation(self, node: ast.Call):
        """Detecta threading.Thread(target=...)"""
        if isinstance(node.func, ast.Attribute):
            if (hasattr(node.func.value, 'id') and 
                node.func.value.id == 'threading' and 
                node.func.attr == 'Thread'):
                
                target_func = None
                thread_name = None

                for keyword in node.keywords:
                    if keyword.arg == 'target':
                        if isinstance(keyword.value, ast.Name):
                            target_func = keyword.value.id
                            thread_name = target_func  # 💡 usamos el nombre de la función
                    elif keyword.arg == 'name':
                        if isinstance(keyword.value, ast.Constant):
                            thread_name = keyword.value.value

                # Si no hay nombre explícito, usamos el target como nombre
                if not thread_name and target_func:
                    thread_name = target_func

                if target_func:
                    self.threads[thread_name] = ThreadInfo(
                        name=thread_name,
                        created_at_line=node.lineno,
                        target_function=target_func,
                        locks_used=set()
                    )
    def _check_with_statements(self, tree: ast.AST):
        """Detecta uso de 'with lock:' como adquisición/liberación de lock"""
        for node in ast.walk(tree):
            if isinstance(node, ast.With):
                for item in node.items:
                    if isinstance(item.context_expr, ast.Name):
                        resource = item.context_expr.id
                        self.resources.add(resource)

                        # Crear una operación de tipo 'acquire'
                        op = LockOperation(
                            thread=self.current_function,
                            resource=resource,
                            action='acquire',
                            line=node.lineno,
                            function=self.current_function
                        )
                        self.operations.append(op)

    def _check_lock_operation(self, node: ast.Call):
        """Detecta lock.acquire() y lock.release()"""
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in ['acquire', 'release']:
                if isinstance(node.func.value, ast.Name):
                    resource_name = node.func.value.id
                    self.resources.add(resource_name)
                    
                    operation = LockOperation(
                        thread=self.current_function,
                        resource=resource_name,
                        action=node.func.attr,
                        line=node.lineno,
                        function=self.current_function
                    )
                    self.operations.append(operation)
    
    def _check_lock_declaration(self, node: ast.Assign):
        """Detecta lock_a = threading.Lock()"""
        if isinstance(node.value, ast.Call):
            if isinstance(node.value.func, ast.Attribute):
                if (hasattr(node.value.func.value, 'id') and 
                    node.value.func.value.id == 'threading' and 
                    node.value.func.attr == 'Lock'):
                    
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            self.resources.add(target.id)
    
    def _generate_report(self) -> Dict:
        """Genera reporte estructurado del análisis"""
        return {
            "threads": {name: {
                "name": info.name,
                "created_at_line": info.created_at_line,
                "target_function": info.target_function,
                "locks_used": list(info.locks_used)
            } for name, info in self.threads.items()},
            "resources": list(self.resources),
            "operations": [asdict(op) for op in self.operations],
            "summary": {
                "total_threads": len(self.threads),
                "total_resources": len(self.resources),
                "total_operations": len(self.operations)
            }
        }
    
    def export_to_json(self, output_path: str):
        """Exporta resultados a JSON"""
        report = self._generate_report()
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print(f"✓ Análisis exportado a: {output_path}")


# Ejemplo de uso
if __name__ == "__main__":
    analyzer = CodeAnalyzer()
    
    # Analizar archivo de ejemplo
    results = analyzer.analyze_file("examples/deadlock_example.py")
    
    # Exportar resultados
    analyzer.export_to_json("reports/analysis_output.json")
    
    # Mostrar resumen
    print("\n📊 RESUMEN DEL ANÁLISIS:")
    print(f"   Threads detectados: {results['summary']['total_threads']}")
    print(f"   Recursos (locks): {results['summary']['total_resources']}")
    print(f"   Operaciones totales: {results['summary']['total_operations']}")