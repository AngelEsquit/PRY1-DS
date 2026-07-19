# Proyecto 1 — Obtención y limpieza de datos

El pipeline parte de archivos `.xls` de MINEDUC y conserva cada etapa para
que el diagnóstico y la limpieza puedan repetirse al actualizar la fuente.

## Estructura

- `Data/raw/`: archivos fuente descargados, sin modificar.
- `Data/csv/`: conversiones por departamento, consolidado y dataset limpio.
- `Data/Diagnosticos/`: tablas generadas en el diagnóstico.
- `notebooks/`: ejecución documentada y ordenada del proyecto.
- `tests/`: validaciones automáticas del dataset limpio.
- `Reportes/`: evidencia de transformaciones, calidad y duplicados a revisar.

## Orden de ejecución

1. `notebooks/00_descarga_datos.ipynb` — punto reservado para la descarga
   automática de los `.xls` desde el portal del MINEDUC.
2. `notebooks/01_diagnostico_inicial.ipynb` — convierte los XLS a CSV y
   genera las tablas de diagnóstico inicial.
3. `notebooks/02_limpieza_y_validacion.ipynb` — aplica las reglas de limpieza
   y exporta el dataset limpio.

## Instalación

```powershell
py -m pip install -r requirements.txt
```

> **Nota sobre los archivos `.xls`**
> Los archivos del portal del MINEDUC son páginas HTML exportadas con
> extensión `.xls` (no hojas binarias de Excel). El notebook 01 los parsea
> directamente con el módulo `html.parser` de la librería estándar de Python.
> **No se necesita LibreOffice ni ninguna dependencia adicional.**
> El proceso completo de conversión de los 23 departamentos tarda ~1–2 segundos.

## Pruebas automáticas

```powershell
py -m pytest tests/ -v
```

Cubre: sin duplicados exactos · sin espacios al borde · dominios de
variables categóricas · formato de CODIGO · departamentos en catálogo ·
teléfonos con dígitos únicamente · categorías sin mezcla de mayúsculas ·
tipos de datos esperados.

