# 🔍 Detector Inteligente de Deadlocks

Sistema multi-nivel de detección, análisis y corrección automática de deadlocks con aprendizaje adaptativo.

## 🌟 Características

- **Análisis Multi-Nivel**: 4 niveles de análisis (estático, flujo de control, contextual, probabilístico)
- **Grafo RAG**: Construcción y análisis de Resource Allocation Graph
- **Detección Automática**: Identificación de ciclos y patrones de deadlock
- **Simulador Integrado**: Validación mediante simulación de escenarios
- **Recomendaciones Inteligentes**: Múltiples estrategias de corrección con trade-offs
- **Base de Conocimiento**: Aprendizaje incremental de patrones

## 📦 Instalación

```bash
pip install -r requirements.txt
```

## 🚀 Uso Básico

```bash
# Analizar un archivo
python src/cli.py analyze examples/deadlock_example.py

# Modo verbose
python src/cli.py analyze code.py --verbose
```

## 📊 Estructura del Proyecto

```
deadlock-intelligent-detector/
├── src/
│   ├── analyzer/         # Análisis sintáctico
│   ├── detector/         # Detección de deadlocks
│   ├── simulator/        # Simulación de escenarios
│   ├── recommender/      # Motor de recomendaciones
│   ├── knowledge/        # Base de conocimiento
│   ├── performance/      # Análisis de rendimiento
│   └── cli.py           # Interfaz de línea de comandos
├── reports/             # Reportes generados
├── examples/            # Ejemplos de código
├── tests/               # Tests unitarios
└── data/                # Datos y patrones
```

## 🧪 Tests

```bash
pytest tests/
```

## 📚 Documentación

Ver documentación completa en `/docs`

## 🎯 Roadmap

- [x] Análisis sintáctico básico
- [x] Construcción de RAG
- [x] Detección de ciclos
- [ ] Simulador de escenarios
- [ ] Motor de recomendaciones
- [ ] Sistema de aprendizaje
- [ ] Análisis de performance

## 👥 Contribuciones

Contribuciones son bienvenidas. Por favor lee CONTRIBUTING.md

## 📄 Licencia

MIT License - ver LICENSE para detalles
