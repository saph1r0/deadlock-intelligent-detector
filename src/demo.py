"""
Demo Interactiva del Detector
FASE 8: Permite al usuario probar el sistema paso a paso
"""

import argparse
from analyzer import CodeAnalyzer
from detector import DeadlockDetector
from recommender import Recommender
from knowledge_base import KnowledgeBase

def run_demo(file: str, interactive: bool = False):
    analyzer = CodeAnalyzer()
    detector = DeadlockDetector()
    recommender = Recommender()
    kb = KnowledgeBase()

    print("\n╔═══════════════════════════════════════════════════════════╗")
    print("║   🔍 DETECTOR INTELIGENTE DE DEADLOCKS v1.0              ║")
    print("╚═══════════════════════════════════════════════════════════╝")

    print(f"\n📁 Analizando: {file}")
    results = analyzer.analyze_file(file)
    det_result = detector.analyze(results["operations"])

    print("\n--- RESUMEN ---")
    print(f"Threads: {results['summary']['total_threads']}")
    print(f"Recursos: {results['summary']['total_resources']}")
    print(f"Operaciones: {results['summary']['total_operations']}")

    if det_result["deadlocks_detected"] > 0:
        print(f"\n⚠️  DEADLOCK DETECTADO ({det_result['deadlocks_detected']})")
        pattern_id = "classic_two_thread"

        kb.register_detection(pattern_id, file,
                              list(results["threads"].keys()),
                              list(results["resources"]))

        recs = recommender.recommend(pattern_id)
        print("\n💡 Estrategias sugeridas:")
        for i, sol in enumerate(recs["top_solutions"], 1):
            print(f"  {i}. {sol['name']} (Score: {sol['score']}/100)")

    else:
        print("\n✅ No se detectaron deadlocks.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Demo del Detector de Deadlocks")
    parser.add_argument("file", nargs="?", default="examples/deadlock_example.py")
    parser.add_argument("--interactive", action="store_true", help="Ejecutar en modo interactivo")
    args = parser.parse_args()

    run_demo(args.file, args.interactive)
