"""
Prueba unitaria para el módulo analyzer.py
Verifica que el analizador detecta hilos, recursos y operaciones correctamente.
"""

import os
import sys
import pytest

# Agregar el path de src/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from analyzer import CodeAnalyzer

EXAMPLE_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../examples/deadlock_example.py"))

def test_analyzer_basic():
    analyzer = CodeAnalyzer()
    results = analyzer.analyze_file(EXAMPLE_FILE)

    # Validar estructura de resultados
    assert isinstance(results, dict)
    assert "threads" in results
    assert "resources" in results
    assert "operations" in results
    assert "summary" in results

    # Validar que detecte al menos 2 hilos
    assert results["summary"]["total_threads"] >= 2

    # Validar que haya recursos (locks)
    assert results["summary"]["total_resources"] >= 2

    # Validar operaciones detectadas
    assert results["summary"]["total_operations"] > 0

    # Validar que cada operación tenga las claves esperadas
    for op in results["operations"]:
        assert "thread" in op
        assert "resource" in op
        assert "action" in op

def test_analyzer_thread_names():
    analyzer = CodeAnalyzer()
    results = analyzer.analyze_file(EXAMPLE_FILE)

    # Asegurarse de que se detecten nombres de hilos esperados
    thread_names = list(results["threads"].keys())
    assert any("thread_function_1" in t for t in thread_names)
    assert any("thread_function_2" in t for t in thread_names)

if __name__ == "__main__":
    pytest.main(["-v", __file__])
