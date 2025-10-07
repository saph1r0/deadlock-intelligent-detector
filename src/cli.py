"""
CLI Minimalista para Detector de Deadlocks
Interfaz simple y funcional con colores
"""

import sys
import argparse
from pathlib import Path

# Importar módulos del proyecto
from analyzer import CodeAnalyzer
from detector import MultiLevelDeadlockDetector
from recommender import DeadlockRecommender
from knowledge_base import KnowledgeBase


# Colores ANSI simples
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_header():
    """Imprime header del programa"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}🔍 DETECTOR INTELIGENTE DE DEADLOCKS{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")


def analyze_file(filepath: str):
    """Pipeline completo de análisis"""
    
    print_header()
    
    # Validar archivo
    if not Path(filepath).exists():
        print(f"{Colors.RED}❌ Error: Archivo '{filepath}' no encontrado{Colors.END}")
        sys.exit(1)
    
    print(f"📁 Analizando: {Colors.BOLD}{filepath}{Colors.END}\n")
    
    # PASO 1: Análisis sintáctico
    print(f"{Colors.YELLOW}🔎 [PASO 1/4] Análisis sintáctico...{Colors.END}")
    analyzer = CodeAnalyzer()
    analysis_result = analyzer.analyze_file(filepath)
    analyzer.export_to_json("reports/analysis_output.json")
    
    print(f"   {Colors.GREEN}✓{Colors.END} Threads detectados: {analysis_result['summary']['total_threads']}")
    print(f"   {Colors.GREEN}✓{Colors.END} Recursos (locks): {analysis_result['summary']['total_resources']}")
    print(f"   {Colors.GREEN}✓{Colors.END} Operaciones: {analysis_result['summary']['total_operations']}\n")
    
    # PASO 2: Detección de deadlocks
    print(f"{Colors.YELLOW}🔍 [PASO 2/4] Detección de deadlocks...{Colors.END}")
    detector = MultiLevelDeadlockDetector()
    detector.load_analysis("reports/analysis_output.json")
    deadlock_report = detector.analyze()
    detector.export_report("reports/deadlock_report.json")
    
    total_deadlocks = deadlock_report['total_deadlocks_detected']
    
    if total_deadlocks > 0:
        print(f"\n   {Colors.RED}⚠️  DEADLOCKS DETECTADOS: {total_deadlocks}{Colors.END}")
        for severity, count in deadlock_report['by_severity'].items():
            if count > 0:
                print(f"      • {severity}: {count}")
    else:
        print(f"   {Colors.GREEN}✓ No se detectaron deadlocks{Colors.END}")
    
    print()
    
    # PASO 3: Generar recomendaciones (si hay deadlocks)
    if total_deadlocks > 0:
        print(f"{Colors.YELLOW}💡 [PASO 3/4] Generando recomendaciones...{Colors.END}")
        recommender = DeadlockRecommender()
        recommendations = recommender.recommend(deadlock_report)
        recommender.print_summary(recommendations)
        recommender.generate_report(recommendations, "reports/recommendations.md")
    else:
        print(f"{Colors.YELLOW}💡 [PASO 3/4] Sin recomendaciones (no hay deadlocks){Colors.END}\n")
    
    # PASO 4: Actualizar base de conocimiento
    print(f"{Colors.YELLOW}📚 [PASO 4/4] Actualizando base de conocimiento...{Colors.END}")
    kb = KnowledgeBase()
    
    if total_deadlocks > 0:
        for i, deadlock in enumerate(deadlock_report.get('deadlocks', []), start=1):
            threads = deadlock.get('threads_involved', []) or deadlock.get('threads', [])
            resources = deadlock.get('resources_involved', []) or deadlock.get('resources', [])
            severity = deadlock.get('severity', 'UNKNOWN')

            kb.register_detection(
                pattern_id=f"detected_pattern_{i}",
                filename=filepath,
                threads=threads,
                resources=resources,
                notes=f"Detected {severity} severity deadlock"
            )

    
    stats = kb.get_all_statistics()
    print(f"   {Colors.GREEN}✓{Colors.END} Patrones registrados: {stats['total_patterns']}")
    print(f"   {Colors.GREEN}✓{Colors.END} Detecciones totales: {stats['total_detections']}\n")
    
    # Resumen final
    print(f"{Colors.BOLD}{Colors.GREEN}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}✅ ANÁLISIS COMPLETADO{Colors.END}")
    print(f"{Colors.BOLD}{Colors.GREEN}{'='*60}{Colors.END}\n")
    
    print("📊 Reportes generados:")
    print(f"   • reports/analysis_output.json")
    print(f"   • reports/deadlock_report.json")
    if total_deadlocks > 0:
        print(f"   • reports/recommendations.md")
    print()


def interactive_mode():
    """Modo interactivo simple"""
    print_header()
    print(f"{Colors.BOLD}Modo Interactivo{Colors.END}")
    print("Escribe 'exit' para salir\n")
    
    while True:
        try:
            filepath = input(f"{Colors.BLUE}Archivo a analizar:{Colors.END} ").strip()
            
            if filepath.lower() in ['exit', 'quit', 'q']:
                print(f"\n{Colors.GREEN}👋 ¡Hasta luego!{Colors.END}\n")
                break
            
            if filepath:
                analyze_file(filepath)
                print("\n" + "="*60 + "\n")
        
        except KeyboardInterrupt:
            print(f"\n\n{Colors.YELLOW}Interrumpido por el usuario{Colors.END}\n")
            break
        except Exception as e:
            print(f"\n{Colors.RED}❌ Error: {e}{Colors.END}\n")


def main():
    """Punto de entrada principal"""
    parser = argparse.ArgumentParser(
        description='Detector Inteligente de Deadlocks',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python cli.py analyze example.py        # Analizar un archivo
  python cli.py -i                        # Modo interactivo
        """
    )
    
    parser.add_argument(
        'command',
        nargs='?',
        choices=['analyze'],
        help='Comando a ejecutar'
    )
    
    parser.add_argument(
        'file',
        nargs='?',
        help='Archivo Python a analizar'
    )
    
    parser.add_argument(
        '-i', '--interactive',
        action='store_true',
        help='Modo interactivo'
    )
    
    args = parser.parse_args()
    
    # Modo interactivo
    if args.interactive:
        interactive_mode()
        return
    
    # Análisis de archivo
    if args.command == 'analyze' and args.file:
        analyze_file(args.file)
        return
    
    # Si no hay argumentos, mostrar ayuda
    parser.print_help()


if __name__ == "__main__":
    main()