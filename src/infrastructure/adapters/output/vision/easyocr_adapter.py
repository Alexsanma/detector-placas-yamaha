import re
import cv2
import easyocr
import numpy as np

from src.application.ports.output.lector_ocr_port import LecturaOCR, LectorOcrPort


# Allowlist: solo caracteres válidos en placas colombianas
_ALLOWLIST = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

# Confusiones OCR típicas en la zona numérica de la placa (posiciones 3 y 4)
_A_NUMERO = {"O": "0", "Q": "0", "D": "0", "I": "1", "S": "5", "B": "8", "Z": "2"}


class EasyOcrAdapter(LectorOcrPort):
    """
    Adaptador de lectura OCR usando EasyOCR.

    Responsabilidades:
    1. Leer caracteres alfanuméricos del recorte de placa.
    2. Ordenar lecturas de izquierda a derecha.
    3. Aplicar regex para extraer el patrón de placa colombiana.
    4. Corregir confusiones OCR según el formato (AAA000 o AAA00A).
    """

    def __init__(
        self,
        idiomas: list[str] | None = None,
        usar_gpu: bool = True,
        umbral_confianza_lectura: float = 0.3,
    ):
        self._reader = easyocr.Reader(idiomas or ["en"], gpu=usar_gpu)
        self._umbral_confianza_lectura = umbral_confianza_lectura

    def leer(self, recorte_bytes: bytes) -> LecturaOCR:
        # Decodificar bytes a imagen OpenCV
        nparr = np.frombuffer(recorte_bytes, np.uint8)
        imagen = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if imagen is None:
            return LecturaOCR(texto="", confianza=0.0)

        # Leer con EasyOCR
        lecturas = self._reader.readtext(
            imagen,
            detail=1,
            allowlist=_ALLOWLIST,
            paragraph=False,
            text_threshold=0.6,
            low_text=0.4,
            mag_ratio=1.5,
        )

        if not lecturas:
            return LecturaOCR(texto="", confianza=0.0)

        # Filtrar por confianza mínima
        lecturas_validas = [l for l in lecturas if l[2] >= self._umbral_confianza_lectura]
        if not lecturas_validas:
            return LecturaOCR(texto="", confianza=0.0)

        # Ordenar de izquierda a derecha por coordenada X del bounding box
        lecturas_validas.sort(key=lambda l: min(p[0] for p in l[0]))

        # Concatenar y limpiar caracteres no alfanuméricos
        texto_crudo = "".join(l[1] for l in lecturas_validas).upper()
        texto_limpio = re.sub(r"[^A-Z0-9]", "", texto_crudo)

        # Extraer patrón de placa colombiana (AAA000 o AAA00A)
        match = re.search(r"[A-Z]{3}[0-9]{2,3}[A-Z]?", texto_limpio)
        if match:
            texto_final = self._corregir_posicion_numerica(match.group())
        elif len(texto_limpio) >= 6:
            texto_final = self._corregir_posicion_numerica(texto_limpio[:6])
        else:
            texto_final = texto_limpio

        # Confianza promedio de las lecturas validadas
        confianza_promedio = sum(l[2] for l in lecturas_validas) / len(lecturas_validas)

        return LecturaOCR(texto=texto_final, confianza=float(confianza_promedio))

    @staticmethod
    def _corregir_posicion_numerica(texto: str) -> str:
        """
        Corrige confusiones OCR en posiciones 3 y 4, que en el formato colombiano
        son siempre números. Ejemplo: 'AURS42' -> 'AUR542'.
        """
        if len(texto) < 5:
            return texto
        chars = list(texto)
        for i in (3, 4):
            if chars[i] in _A_NUMERO:
                chars[i] = _A_NUMERO[chars[i]]
        return "".join(chars)