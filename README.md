# Proyecto 1 — Obtención y limpieza de datos

Pipeline reproducible sobre los establecimientos de nivel diversificado del
MINEDUC: descarga, diagnóstico, limpieza y validación.

## Integrantes

- Javier España — #23361
- Ángel Esquit — #23221
- Roberto Barreda — #23354

## Estructura

- `Data/raw/`: archivos `.xls` fuente, sin modificar.
- `Data/csv/`: CSV por departamento, consolidado y dataset limpio.
- `Data/Diagnosticos/`: tablas del diagnóstico inicial.
- `notebooks/`: ejecución ordenada del proyecto.
- `tests/`: validaciones automáticas del dataset limpio.
- `Reportes/`: transformaciones, informe de calidad y duplicados a revisar.
- `Libro_de_Codigos.md` / `.pdf`: diccionario de variables y metadatos.

## Uso

```powershell
py -m pip install -r requirements.txt
```

Ejecutar los notebooks en orden:

1. `00_descarga_datos.ipynb` — descarga los `.xls` desde el portal del MINEDUC.
2. `01_diagnostico_inicial.ipynb` — convierte los XLS a CSV y genera el diagnóstico.
3. `02_limpieza_y_validacion.ipynb` — aplica la limpieza y exporta el dataset limpio.

Los `.xls` del portal son HTML con extensión `.xls`; se parsean con la
librería estándar, sin LibreOffice ni dependencias externas.

## Pruebas

```powershell
py -m pytest tests/ -v
```
