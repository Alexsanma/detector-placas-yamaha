class PlacaNoDetectadaError(Exception):
    """Se lanza si Yolo no detecta ninguna placa """
    pass


class ConfianzaBajaError(Exception):
    """Se lanza si la confianza es menor al umbral mínimo"""
    pass


class VehiculoNoEncontradoError(Exception):
    """Se lanza cuando no se encuentra el vehículo"""
    pass