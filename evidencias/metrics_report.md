# Reporte de Métricas — Detector de Placas Vehiculares

## Dataset
- Total imágenes: 281
- Train: 195 -- Valid: 56 -- Test: 31
- placa_carro: 248 anotaciones --  placa_moto: 43 anotaciones

## Modelos Entrenados

### v1 — Entrenamiento base (modelo definitivo)
**Configuración:** YOLOv8n, 50 épocas, imgsz=416, batch=2, Transfer Learning desde yolov8n.pt

---
<table>
  <tr>
    <th>Métrica</th>
    <th>Validación</th>
    <th>Test</th>
  </tr>
  <tr>
    <td>mAP50</td>
    <td>97.4%</td>
    <td>82.1%</td>
  </tr>
  <tr>
    <td>mAP50-95</td>
    <td>78.5%</td>
    <td>69.3%</td>
  </tr>
  <tr>
    <td>Precision</td>
    <td>86.6%</td>
    <td>81.8%</td>
  </tr>
  <tr>
    <td>Recall</td>
    <td>100%</td>
    <td>79.8%</td>
  </tr>
</table>
---

### v2 — Fine-tuning con augmentation mejorado
**Configuración:** Fine-tuning desde best.pt, degrees=15, erasing=0.5, flipud=0.1, copy_paste=0.1

---
<table>
  <tr>
    <th>Métrica</th>
    <th>Validación</th>
    <th>Test</th>
  </tr>
  <tr>
    <td>mAP50</td>
    <td>96.6%</td>
    <td>83.4%</td>
  </tr>
  <tr>
    <td>mAP50-95</td>
    <td>71.3%</td>
    <td>58.7%</td>
  </tr>
  <tr>
    <td>Precision</td>
    <td>89.1%</td>
    <td>72.9%</td>
  </tr>
  <tr>
    <td>Recall</td>
    <td>93.4%</td>
    <td>80.6%</td>
  </tr>
</table>
---

### v3 — Desde yolov8n.pt con augmentation mejorado

---
<table>
  <tr>
    <th>Métrica</th>
    <th>Validación</th>
    <th>Test</th>
  </tr>
  <tr>
    <td>mAP50</td>
    <td>95.6%</td>
    <td>78.9%</td>
  </tr>
  <tr>
    <td>mAP50-95</td>
    <td>73.6%</td>
    <td>56.9%</td>
  </tr>
  <tr>
    <td>Precision</td>
    <td>85.4%</td>
    <td>69.9%</td>
  </tr>
  <tr>
    <td>Recall</td>
    <td>97.3%</td>
    <td>77.4%</td>
  </tr>
</table>
---

## Modelo Seleccionado: v1
- Mejor precision en test (81.8%) — menos falsos positivos en BD
- Mejor mAP50-95 en test (69.3%) — bounding boxes más precisos para OCR
- Menor gap de generalización (9.2 pts vs 12.6 pts de v2)

## Limitaciones Identificadas
- Menor rendimiento en placas de moto (mAP50: 70.9%) por desbalance del dataset
- Confusión V → J en condiciones de baja iluminación
- Reflejos fuertes degradan la lectura OCR