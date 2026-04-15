import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Configuración centralizada de la aplicación."""

    # Rutas
    modelo_yolo_path: str
    database_url: str

    # Detección
    umbral_confianza_deteccion: float
    recorte_superior_pct: float
    factor_escala_ocr: float

    # OCR
    idiomas_ocr: list[str]
    usar_gpu: bool
    umbral_confianza_ocr: float

    # Persistencia
    usar_base_datos: bool  # True=SQLite, False=in-memory
    camara_por_defecto: int


def cargar_settings() -> Settings:
    """Carga la configuración desde variables de entorno con defaults sensatos."""
    raiz = Path(__file__).resolve().parents[3]  # raíz del proyecto

    return Settings(
        modelo_yolo_path=os.getenv("MODELO_YOLO_PATH", str(raiz / "models" / "best.pt")),
        database_url=os.getenv("DATABASE_URL", f"sqlite:///{raiz / 'detector_placas.db'}"),
        umbral_confianza_deteccion=float(os.getenv("UMBRAL_CONFIANZA_DETECCION", "0.5")),
        recorte_superior_pct=float(os.getenv("RECORTE_SUPERIOR_PCT", "0.70")),
        factor_escala_ocr=float(os.getenv("FACTOR_ESCALA_OCR", "3.0")),
        idiomas_ocr=os.getenv("IDIOMAS_OCR", "en").split(","),
        usar_gpu=os.getenv("USAR_GPU", "true").lower() == "true",
        umbral_confianza_ocr=float(os.getenv("UMBRAL_CONFIANZA_OCR", "0.3")),
        usar_base_datos=os.getenv("USAR_BASE_DATOS", "true").lower() == "true",
        camara_por_defecto=int(os.getenv("CAMARA_POR_DEFECTO", "1")),
    )