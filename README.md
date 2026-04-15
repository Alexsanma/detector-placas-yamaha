
# Detector de Placas Vehiculares

Sistema de control de acceso vehicular basado en visión por computadora. Detecta placas en imágenes, lee los caracteres, clasifica eventos de ingreso/salida y persiste el historial para trazabilidad.

Prueba técnica para el rol de **Auxiliar de Nuevas Tecnologías** — División de TI, Incolmotos Yamaha.

---
## Cobertura de tareas requeridas

<table>
  <tr>
    <th>#</th>
    <th>Tarea</th>
    <th>Dónde está</th>
  </tr>
  <tr>
    <td>1</td>
    <td><strong>Preprocesamiento de datos</strong> — exploración, limpieza, validación de anotaciones, conversión de formatos, división estratificada</td>
    <td><a href="notebooks/01_exploracion.ipynb">notebooks/01_exploracion.ipynb</a></td>
  </tr>
  <tr>
    <td>2</td>
    <td><strong>Entrenamiento del modelo</strong> — YOLOv8 + EasyOCR, 3 versiones entrenadas y comparadas</td>
    <td><a href="notebooks/02_entrenamiento.ipynb">notebooks/02_entrenamiento.ipynb</a></td>
  </tr>
  <tr>
    <td>3</td>
    <td><strong>Mejora de robustez</strong> — data augmentation documentado (hsv, mosaic, erasing, rotación, copy-paste)</td>
    <td><a href="notebooks/02_entrenamiento.ipynb">notebooks/02_entrenamiento.ipynb</a></td>
  </tr>
  <tr>
    <td>4</td>
    <td><strong>Evaluación</strong> — métricas completas en test (mAP50, mAP50-95, Precision, Recall) por clase</td>
    <td><a href="notebooks/02_entrenamiento.ipynb">notebooks/02_entrenamiento.ipynb</a></td>
  </tr>
  <tr>
    <td>5</td>
    <td><strong>Lógica de negocio</strong> — clasificación ingreso/salida, visitante/registrado/desconocido con reglas de dominio puras</td>
    <td><a href="src/domain/">src/domain/</a></td>
  </tr>
  <tr>
    <td>6</td>
    <td><strong>Buenas prácticas</strong> — arquitectura hexagonal, SOLID, excepciones de dominio, código documentado</td>
    <td><a href="src/">src/</a></td>
  </tr>
  <tr>
    <td>7</td>
    <td><strong>Bonus: persistencia y trazabilidad</strong> — eventos con placa, fecha, tipo, confianza y cámara en SQLite</td>
    <td><a href="src/infrastructure/adapters/output/persistence/">src/infrastructure/.../persistence/</a></td>
  </tr>
  <tr>
    <td>—</td>
    <td><strong>Preguntas de razonamiento (30%) y pregunta abierta (10%)</strong></td>
    <td><a href="#respuestas-a-preguntas-de-razonamiento">Ver respuestas</a></td>
  </tr>
</table>
---

## Tabla de contenidos

1. [Stack tecnológico](#stack-tecnológico)
2. [Arquitectura](#arquitectura)
3. [Instalación](#instalación)
4. [Ejecución](#ejecución)
5. [Uso de la API](#uso-de-la-api)
6. [Decisiones técnicas](#decisiones-técnicas)
7. [Métricas del modelo](#métricas-del-modelo)
8. [Proceso iterativo del OCR](#proceso-iterativo-del-ocr)
9. [Respuestas a preguntas de razonamiento](#respuestas-a-preguntas-de-razonamiento)
10. [Evidencias](#evidencias)
11. [Limitaciones encontradas](#limitaciones-encontradas)
12. [Mejoras Futuras](#mejoras-futuras)
12. [Estructura del proyecto](#estructura-del-proyecto)

---

## Stack tecnológico

- **Python 3.11**
- **YOLOv8** (Ultralytics) — detección de placas
- **EasyOCR** — lectura de caracteres
- **FastAPI** — API REST
- **Streamlit** — interfaz visual
- **SQLAlchemy 2.0 + SQLite** — persistencia
- **Pydantic** — validación de entradas/salidas HTTP

---

## Arquitectura

El proyecto implementa **arquitectura hexagonal (puertos y adaptadores)** con separación clara entre dominio, aplicación e infraestructura.

### ¿Por qué arquitectura hexagonal?

Para un sistema de control de acceso vehicular, la lógica de negocio (clasificación de eventos, reglas de acceso, tipos de vehículo) debe ser independiente de:

- El modelo de detección (YOLO hoy, podría ser Detectron2 mañana)
- El motor OCR (EasyOCR hoy, podría ser PaddleOCR o Tesseract)
- El medio de persistencia (SQLite para desarrollo, PostgreSQL en producción, memoria para tests)
- El punto de entrada (API REST, interfaz Streamlit, o eventualmente un worker de cámaras IP)

Esta separación permite cambiar cualquier componente de infraestructura modificando **una sola línea** en el container, sin impactar la lógica de negocio.

### Capas
---
<table>
  <tr>
    <th colspan="3" align="center">INFRASTRUCTURE (adaptadores)</th>
  </tr>
  <tr>
    <td align="center">FastAPI · Streamlit</td>
    <td align="center">YOLO + EasyOCR (Ultralytics)</td>
    <td align="center">SQLite / Memory (SQLAlchemy)</td>
  </tr>
  <tr>
    <th colspan="3" align="center">APPLICATION (puertos + casos de uso)</th>
  </tr>
  <tr>
    <td colspan="3" align="center">ProcesarDeteccionUseCase · RegistrarVehiculoUseCase · ConsultarEventosUseCase</td>
  </tr>
  <tr>
    <th colspan="3" align="center">DOMAIN (entidades + reglas de negocio puras)</th>
  </tr>
  <tr>
    <td colspan="3" align="center">Vehiculo · Evento · access_rules · excepciones</td>
  </tr>
</table>
---

**Regla de dependencias:** infraestructura depende de aplicación, aplicación depende de dominio. El dominio no depende de nada externo.

### Configuración intercambiable

Cambiar entre SQLite e in-memory se hace con una variable de entorno:

```bash
# .env
USAR_BASE_DATOS=true   # SQLite persistente
USAR_BASE_DATOS=false  # memoria volátil (útil para tests)
```

El container lee esta variable y ensambla los adaptadores correspondientes. Ni el dominio ni los casos de uso se enteran del cambio.

---

## Instalación

**Requisitos:** Python 3.11, CUDA 12.1 (opcional, para aceleración GPU).

```bash
# Clonar el repositorio
git clone <https://github.com/Alexsanma/detector-placas-yamaha.git>
cd detector_placas

# Crear entorno conda
conda create -n detector_placas python=3.11
conda activate detector_placas

# Instalar PyTorch según tu hardware
# GPU (CUDA 12.1):
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
# CPU:
pip install torch torchvision

# Instalar el resto de dependencias
pip install -r requirements.txt
```

**Configuración:** copia `.env.example` a `.env` y ajusta los valores si es necesario. Los defaults funcionan sin modificar nada.

---

## Ejecución

El sistema tiene dos componentes: API backend y frontend Streamlit. Puedes correr uno o ambos.

### Opción 1: API + Streamlit (recomendado)

**Terminal 1 — Backend:**
```bash
conda activate detector_placas
uvicorn main:app --reload
```

Disponible en `http://127.0.0.1:8000` · Documentación Swagger en `/docs`.

**Terminal 2 — Streamlit:**
```bash
conda activate detector_placas
streamlit run streamlit_app.py
```

Disponible en `http://localhost:8501`.

### Opción 2: Solo API

```bash
uvicorn main:app --reload
```

Interactúa con los endpoints desde Swagger UI en `/docs`, Postman, o `curl`.


## Uso de la API

### `POST /detectar`
Sube una imagen, detecta la placa y registra el evento.

**Parámetros:**
- `imagen` (multipart file, requerido)
- `camera_id` (query param, opcional — default 1)

**Respuesta 200:**
```json
{
  "evento_id": 1,
  "placa": "CET337",
  "tipo_evento": "ingreso",
  "tipo_vehiculo": "visitante",
  "confianza_deteccion": 0.91,
  "confianza_ocr": 0.76,
  "fecha_hora": "2026-04-13T00:23:36",
  "camera_id": 1
}
```

### `POST /vehiculos`
Registra un vehículo autorizado.

```json
{
  "placa": "CET337",
  "tipo": "registrado",
  "nombre": "Propietario"
}
```

### `GET /eventos`
Lista el historial completo de eventos ordenado por fecha descendente.

---

## Decisiones técnicas

---
### 1. Preprocesamiento y exploración del dataset

El dataset original de Roboflow contenía 281 imágenes con un problema no documentado: las anotaciones mezclaban dos formatos distintos — 154 en formato estándar YOLOv8 (5 datos por línea) y 137 en formato polígono (9-13 datos). Sin conversión, YOLO no podía entrenar correctamente.

**Decisiones tomadas:**
- Dataset original preservado intacto en `data/raw/` — los labels procesados viven en `data/processed/`
- 137 anotaciones en formato polígono convertidas a bounding box calculando el rectángulo mínimo que contiene el polígono
- Redimensionamiento y normalización delegados a YOLO internamente — aplica letterboxing (mantiene proporción + padding) en lugar de resize directo para evitar distorsión
- División estratificada en `data/splits/`: imágenes con una sola placa divididas 70/20/10 por clase, imágenes con múltiples placas e imágenes mixtas distribuidas manualmente para garantizar representación en todos los splits

**Resultado:** 195 train · 56 valid · 31 test

**Observación relevante:** el dataset tiene un desbalance de clases notable — 248 anotaciones de `placa_carro` vs 43 de `placa_moto`. Esto impacta directamente el rendimiento del modelo en motos, como se confirma en las métricas de test (93.4% vs 70.9% de mAP50).

Proceso completo documentado en [`notebooks/01_exploracion.ipynb`](notebooks/01_exploracion.ipynb).
---

### 2. Selección del modelo de detección: v1 sobre v2 o v3

Se entrenaron tres versiones del detector YOLO. Tras comparar métricas sobre el set de **test**:

---

<table>
  <tr>
    <th>Métrica</th>
    <th>v1</th>
    <th>v2</th>
    <th>v3</th>
  </tr>
  <tr>
    <td>mAP50</td>
    <td>82.1%</td>
    <td>83.4%</td>
    <td>78.9%</td>
  </tr>
  <tr>
    <td>mAP50-95</td>
    <td>69.3%</td>
    <td>58.7%</td>
    <td>56.9%</td>
  </tr>
  <tr>
    <td>Precision</td>
    <td>81.8%</td>
    <td>72.9%</td>
    <td>69.9%</td>
  </tr>
  <tr>
    <td>Recall</td>
    <td>79.8%</td>
    <td>80.6%</td>
    <td>77.4%</td>
  </tr>
</table>

---

<table>
  <tr>
    <th>Modelo</th>
    <th>mAP50-95 val</th>
    <th>mAP50-95 test</th>
    <th>Gap</th>
  </tr>
  <tr>
    <td>v1</td>
    <td>78.5%</td>
    <td>69.3%</td>
    <td>9.2 pts</td>
  </tr>
  <tr>
    <td>v2</td>
    <td>71.3%</td>
    <td>58.7%</td>
    <td>12.6 pts</td>
  </tr>
  <tr>
    <td>v3</td>
    <td>73.6%</td>
    <td>56.9%</td>
    <td>16.7 pts</td>
  </tr>
</table>

- v1 tiene un gap de 9.2 puntos: mejor generalización
- v2 tiene un gap de 12.6 puntos: mayor sobreajuste
- v3 tiene un gap de 16.7 puntos: el mayor sobreajuste y menor capacidad de generalizar a datos nuevos

Se selecciona **V1 como modelo definitivo** por las siguientes razones: 

- **1 Mejor generalización**: El gap entre validación y test es el menor (9.2 pts), lo que indica que en realidad aprende patrones reales y no memoriza el datset.

- **2 Mayor precisión en producción**: en un sistema de control de acceso vehicular los falsos positivos son especialmente dañinos por que insertan registros basura en la base de datos de eventos de forma silenciosa y acumulativa, contaminando la trazabilidad. Una precision alta minimiza este riesgo. 

- **3 mejor localización del bounding box (mAP50-95: 69.3%)**: Un bounding box más preciso produce un recorte más limpio de la placa, lo que se traduce directamente en mejor lectura de caracteres que le corresponde al siguiente modelo.  

los modelos v2 y v3 se conservan en el repositorio como una evidencia del proceso iterativo y a su vez como un punto de comparición técnica 

### 3. Stack de visión

- **YOLOv8 (Ultralytics):** balance óptimo entre precisión, velocidad y facilidad de entrenamiento. Comunidad activa y documentación sólida.
- **EasyOCR:** OCR genérico pero robusto, funciona razonablemente bien sin fine-tuning específico de placas. Alternativa evaluada: PaddleOCR (mejor rendimiento teórico pero mayor complejidad de instalación).

### 4. Persistencia con SQLAlchemy 2.0

SQLite fue elegido por simplicidad: no requiere servidor, la base se crea sola, y el archivo `.db` es portable. Para producción, bastaría cambiar el `database_url` en `.env` a PostgreSQL sin tocar ni una línea de los repositorios (gracias a SQLAlchemy).

### 5. Dos implementaciones del repositorio

- `SqliteRepository`: persistencia real vía SQLAlchemy.
- `InMemoryRepository`: almacenamiento volátil en `dict`. Útil para tests rápidos y demos sin BD.

Se intercambian cambiando una variable de entorno (`USAR_BASE_DATOS`).

### 6. Valor por defecto para cámara

El `camera_id` tiene un default configurable (`CAMARA_POR_DEFECTO` en `.env`). Esto evita peticiones inválidas en pruebas manuales y refleja un caso real de una sola cámara por punto de acceso.

---

## Métricas del modelo

**Modelo seleccionado: v1** — YOLOv8n, 50 épocas, imgsz=416, Transfer Learning desde yolov8n.pt.

### Validación
---
<table>
  <tr>
    <th>Métrica</th>
    <th>General</th>
    <th>placa_carro</th>
    <th>placa_moto</th>
  </tr>
  <tr>
    <td>mAP50</td>
    <td>97.4%</td>
    <td>99.0%</td>
    <td>95.9%</td>
  </tr>
  <tr>
    <td>mAP50-95</td>
    <td>78.5%</td>
    <td>73.9%</td>
    <td>83.1%</td>
  </tr>
  <tr>
    <td>Precision</td>
    <td>86.6%</td>
    <td>82.6%</td>
    <td>90.7%</td>
  </tr>
  <tr>
    <td>Recall</td>
    <td>100%</td>
    <td>100%</td>
    <td>100%</td>
  </tr>
</table>
---

### Test (conjunto nunca visto durante el entrenamiento)

<table>
  <tr>
    <th>Métrica</th>
    <th>General</th>
    <th>placa_carro</th>
    <th>placa_moto</th>
  </tr>
  <tr>
    <td>mAP50</td>
    <td>82.1%</td>
    <td>93.4%</td>
    <td>70.9%</td>
  </tr>
  <tr>
    <td>mAP50-95</td>
    <td>69.3%</td>
    <td>75.8%</td>
    <td>62.8%</td>
  </tr>
  <tr>
    <td>Precision</td>
    <td>81.8%</td>
    <td>84.8%</td>
    <td>78.9%</td>
  </tr>
  <tr>
    <td>Recall</td>
    <td>79.8%</td>
    <td>92.9%</td>
    <td>66.7%</td>
  </tr>
</table>
---

El modelo alcanzó un mAP50 de 82.1% en el conjunto de test, lo que demuestra una adecuada capacidad de generalización ante datos no vistos. La caída respecto a validación (97.4% → 82.1%) es esperada dado el tamaño reducido del dataset (195 imágenes de entrenamiento) y representa un leve overfitting controlado.

El modelo es especialmente confiable en la detección de `placa_carro` (mAP50: 93.4%), mientras que `placa_moto` presenta menor rendimiento (70.9%) — atribuible directamente al desbalance del dataset: 248 anotaciones de carro vs 43 de moto.

Detalles completos en [`evidencias/metrics_report.md`](evidencias/metrics_report.md) y [`notebooks/02_entrenamiento.ipynb`](notebooks/02_entrenamiento.ipynb).

## Proceso iterativo del OCR

El pipeline de lectura de placas se afinó en tres iteraciones documentadas en `notebooks/02_evaluacion.ipynb`. Resumen:

1. **Iteración 1 (base):** YOLO + EasyOCR sin procesamiento → acertaba 1-2 de 6 imágenes. Leía el texto inferior de la placa ("ANDALUCIA", "CALI", etc.).
2. **Iteración 2 (preprocesamiento agresivo):** recorte al 60% + binarización Otsu → empeoró. EasyOCR se entrena sobre imágenes naturales, no binarias.
3. **Iteración 3 (final):** recorte al 70% + escalado 3x + allowlist `[A-Z0-9]` + orden de lecturas por coordenada X + corrección contextual por posición → 4-5 de 6 aciertos consistentes.

**Lección clave:** menos preprocesamiento funcionó mejor. El mayor salto de calidad vino de (a) recortar la zona inferior antes del OCR y (b) aplicar conocimiento del formato de placa colombiana como corrección post-OCR.

---
## Respuestas a preguntas de razonamiento

Las respuestas a las preguntas técnicas están documentadas en el siguiente archivo:

- [Preguntas de razonamiento técnico (30%)](https://drive.google.com/file/d/1Md_bIAbbz0HC7pyDtlKVBf1yd7o8hAOl/view?usp=drive_link)
- [Pregunta abierta — Arquitectura sistema real (10%)](https://drive.google.com/file/d/1_pGErm7Uh7bMR0IHUFd8fr0Hom_-LUuo/view?usp=drive_link)
---
## Evidencias

### Detección de placas — YOLO v1
Las siguientes imágenes muestran el modelo definitivo (v1) en acción sobre imágenes del conjunto de test — placas que el modelo nunca vio durante el entrenamiento.

[`evidencias/inference_examples/`](evidencias/inference_examples/)

---

### Pipeline OCR — Proceso iterativo
Se documentaron tres iteraciones del pipeline YOLO + EasyOCR. Cada archivo muestra el estado del OCR en esa iteración, evidenciando la mejora progresiva:

- `pipeline_ocr_iteracion_1` — OCR base sin preprocesamiento. Leía texto inferior de la placa ("ANDALUCIA", "CALI", etc.)
- `pipeline_ocr_iteracion_2` — Preprocesamiento agresivo (binarización Otsu). Empeoró los resultados.
- `pipeline_ocr_iteracion_3` — Versión final: recorte al 70% + escalado 3x + corrección contextual. 4-5 aciertos de 6.

[`evidencias/ocr_examples/`](evidencias/ocr_examples/)

---

### Notebooks documentados

**[`01_exploracion.ipynb`](notebooks/01_exploracion.ipynb)**  
Preprocesamiento de datos: exploración del dataset, validación de anotaciones, conversión de polígonos a bounding box y división estratificada train/valid/test.

**[`02_entrenamiento.ipynb`](notebooks/02_entrenamiento.ipynb)**  
Entrenamiento de 3 modelos YOLO, técnicas de data augmentation, evaluación con métricas completas (mAP50, mAP50-95, Precision, Recall), inferencia visual y pipeline OCR iterativo.

---

## Limitaciones encontradas

1. **Reflejos fuertes del flash:** segmentan visualmente la placa y el OCR puede devolver fragmentos desordenados. Mitigado parcialmente con orden por coordenada X.
2. **Confusiones visuales en zona de letras:** por ejemplo `V` leída como `J` en iluminación baja. Las correcciones contextuales solo aplican a zonas numéricas (posiciones 3 y 4).
3. **Motion blur:** imágenes movidas pierden rasgos distintivos entre caracteres. Requiere super-resolución o modelo OCR específico de placas.
4. **Formato único:** el pipeline asume formato colombiano (`AAA000` carros / `AAA00A` motos). Placas de otros países no se reconocerían correctamente.
5. **Una sola placa por imagen:** el caso de uso selecciona la detección con mayor confianza. Si hay múltiples vehículos en la misma imagen, solo procesa uno.

---
## Mejoras futuras

- **Modelo OCR específico de placas colombianas** — entrenar una CRNN sobre un dataset dedicado de placas colombianas eliminaría las confusiones V→J y O→0 que el OCR genérico no resuelve.
- **Procesamiento de video en tiempo real (RTSP)** — integrar streams de cámaras IP con ensemble de frames: leer la misma placa en N frames consecutivos y elegir la lectura más frecuente para compensar blur y reflejos transitorios.
- **Detección de múltiples placas por imagen** — el caso de uso actual selecciona la detección con mayor confianza. Con tracking entre frames se podrían procesar múltiples vehículos simultáneos.
- **Modelo de corrección contextual más robusto** — las correcciones actuales solo aplican a zonas numéricas (posiciones 3-4). Un clasificador entrenado sobre la tipografía específica de placas colombianas resolvería confusiones en la zona de letras.
- **Dashboard analítico** — estadísticas de acceso: horarios pico, placas recurrentes, vehículos con accesos anómalos, tasa de detecciones fallidas por hora.
- **Migración a PostgreSQL + Redis** — PostgreSQL para alta concurrencia en producción, Redis para cachear el último evento de cada placa y evitar queries repetitivas en la lógica de ingreso/salida.
- **Tests de integración end-to-end** — cubrir el flujo completo con pytest + adaptadores in-memory, sin dependencia de GPU ni BD real.
- **Exportación del modelo a TensorRT** — cuantización FP16 para despliegue en dispositivos edge (Jetson) con 2-4x de aceleración y consumo reducido de VRAM.
- **Alertas automáticas** — notificaciones por webhook o correo cuando se detecte una placa con accesos fuera de horario, placas no registradas con alta frecuencia, o caída sostenida de la confianza del modelo.
---

## Estructura del proyecto

```
detector_placas/
├── main.py                       # entrada FastAPI
├── streamlit_app.py              # interfaz visual
├── test_rapido.py                # script de prueba rápida
├── requirements.txt
├── .env                          # configuración (no versionado)
│
├── data/                         # dataset + splits
├── models/                       # pesos YOLO entrenados (best.pt)
├── notebooks/                    # exploración + evaluación
├── evidencias/                   # imágenes de inferencia + reporte de métricas
│
└── src/
    ├── domain/                   # entidades puras + reglas de negocio
    │   ├── entities/             # Vehiculo, Evento
    │   ├── value_objects/        # TipoEvento, TipoVehiculo
    │   ├── services/             # access_rules
    │   └── exceptions.py
    │
    ├── application/              # casos de uso + puertos
    │   ├── ports/
    │   │   ├── input/            # contratos que ofrece la app
    │   │   └── output/           # contratos que la app necesita del exterior
    │   ├── use_cases/
    │   └── dtos/
    │
    └── infrastructure/           # adaptadores concretos
        ├── adapters/
        │   ├── input/api/        # routers FastAPI + schemas Pydantic
        │   └── output/
        │       ├── vision/       # YOLO + EasyOCR
        │       └── persistence/
        │           ├── sqlite/
        │           └── in_memory/
        └── config/               # settings + container
```

---

## Autor

**Alexander Sanmartin Arredondo**  
Prueba técnica para Incolmotos Yamaha — abril 2026.
```
