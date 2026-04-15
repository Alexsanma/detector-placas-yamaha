```markdown
# Detector de Placas Vehiculares

Sistema de control de acceso vehicular basado en visión por computadora. Detecta placas en imágenes, lee los caracteres, clasifica eventos de ingreso/salida y persiste el historial para trazabilidad.

Prueba técnica para el rol de **Auxiliar de Nuevas Tecnologías** — División de TI, Incolmotos Yamaha.

---

## Tabla de contenidos

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
git clone <url-del-repo>
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

### 1. Selección del modelo de detección: v1 sobre v2 o v3

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

### 2. Stack de visión

- **YOLOv8 (Ultralytics):** balance óptimo entre precisión, velocidad y facilidad de entrenamiento. Comunidad activa y documentación sólida.
- **EasyOCR:** OCR genérico pero robusto, funciona razonablemente bien sin fine-tuning específico de placas. Alternativa evaluada: PaddleOCR (mejor rendimiento teórico pero mayor complejidad de instalación).

### 3. Persistencia con SQLAlchemy 2.0

SQLite fue elegido por simplicidad: no requiere servidor, la base se crea sola, y el archivo `.db` es portable. Para producción, bastaría cambiar el `database_url` en `.env` a PostgreSQL sin tocar ni una línea de los repositorios (gracias a SQLAlchemy).

### 4. Dos implementaciones del repositorio

- `SqliteRepository`: persistencia real vía SQLAlchemy.
- `InMemoryRepository`: almacenamiento volátil en `dict`. Útil para tests rápidos y demos sin BD.

Se intercambian cambiando una variable de entorno (`USAR_BASE_DATOS`).

### 5. Valor por defecto para cámara

El `camera_id` tiene un default configurable (`CAMARA_POR_DEFECTO` en `.env`). Esto evita peticiones inválidas en pruebas manuales y refleja un caso real de una sola cámara por punto de acceso.

---

## Métricas del modelo

**Modelo seleccionado: v1** 

---
<table>
  <tr>
    <th>Métrica</th>
    <th>Valor</th>
  </tr>
  <tr>
    <td>mAP50</td>
    <td>82.1%</td>
  </tr>
  <tr>
    <td>mAP50-95</td>
    <td>69.3%</td>
  </tr>
  <tr>
    <td>Precision</td>
    <td>81.8%</td>
  </tr>
  <tr>
    <td>Recall</td>
    <td>79.8%</td>
  </tr>
</table>
---

Detalles adicionales en `evidencias/metrics_report.md` y notebooks en `notebooks\02_entrenamiento.ipynb`.

---

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
