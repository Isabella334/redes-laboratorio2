# tests/ — pruebas empíricas compartidas

Carpeta común (no pertenece solo a `emisor-python` ni solo a `receptor-go`)
con los scripts que generan los datos y gráficas para la sección de
Resultados/Discusión del reporte. Reutilizan directamente los algoritmos ya
implementados en `emisor-python/algorithms` y `emisor-python/layers` — no
reimplementan nada — para que las cifras reflejen exactamente lo que la
aplicación real envía.

## Requisitos

```bash
pip install matplotlib
```

(Python 3, sin más dependencias.)

## `common.py`

Utilidades compartidas por ambos scripts de prueba: generación de texto
aleatorio reproducible (semilla fija), acceso a `presentation.encode_message`,
y una versión del modelo de ruido bit a bit controlada por un `random.Random`
propio (mismo modelo que `layers/noise.py`, pero determinista entre corridas).

## `test_crc32.py` (Persona 2 — detección de errores)

Barre un grid de **tamaño de mensaje x tasa de error del canal**, con varios
cientos de pruebas independientes por combinación. Por cada prueba: codifica
el texto, calcula el CRC-32, aplica ruido, y verifica si el receptor
detectaría el error. Solo cuenta como "detección esperada" los casos donde el
ruido de verdad alteró al menos un bit (`actual_error`); si el ruido no tocó
ningún bit, ese caso se excluye de la tasa de detección porque no había nada
que detectar.

Genera:

- `results/crc32_raw.csv` — una fila por prueba individual.
- `results/crc32_summary.csv` — agregado por (tamaño, tasa de error): tasa de
  detección, overhead, conteos.
- `plots/crc32_detection_vs_error_rate.png` — tasa de detección vs. tasa de
  error, una serie por tamaño de mensaje.
- `plots/crc32_overhead_vs_size.png` — overhead (%) vs. tamaño del mensaje
  (escala log), mostrando cómo los 32 bits fijos de CRC pesan cada vez menos
  conforme crece el mensaje.

```bash
python3 tests/test_crc32.py
```

Tarda ~35s en una laptop moderna (4 tamaños x 9 tasas de error x 200
pruebas = 7,200 pruebas).

## `test_hamming.py` (Persona 1 — corrección de errores)

Pendiente — sigue el mismo patrón que `test_crc32.py`, pero variando además
`r` (bits de paridad), y midiendo tasa de corrección exitosa (no solo
detección) y overhead como función de `r`.
