# Avances del Proyecto 1

## Resumen del conjunto de datos

El conjunto de datos corresponde a establecimientos educativos autorizados por el MINEDUC para el nivel Diversificado en Guatemala. La fuente original viene en 23 archivos `.xls`, uno por departamento o region, y cada archivo trae una tabla util junto con texto informativo en las primeras filas.

Despues de identificar la fila real de encabezados y aislar la tabla, el volumen inicial observado es de **11,867 registros** y **17 variables**.

Variables detectadas:

- CODIGO
- DISTRITO
- DEPARTAMENTO
- MUNICIPIO
- ESTABLECIMIENTO
- DIRECCION
- TELEFONO
- SUPERVISOR
- DIRECTOR
- NIVEL
- SECTOR
- AREA
- STATUS
- MODALIDAD
- JORNADA
- PLAN
- DEPARTAMENTAL

## Variables que van a requerir mas limpieza

Las columnas con mayor carga de limpieza son:

- TELEFONO: valores faltantes, varios formatos, separadores distintos y algunos registros con caracteres no numericos.
- DIRECTOR: muchos faltantes y valores placeholder como `---`, `--`, `----` o `SIN DATO`.
- SUPERVISOR: diferencias de acentos, mayusculas y espacios multiples.
- ESTABLECIMIENTO: comillas, acentos, variantes ortograficas y diferencias de escritura entre registros equivalentes.
- DIRECCION: abreviaturas, puntuacion inconsistente y varios formatos textuales.
- DISTRITO: faltantes y codigos truncados o incompletos.
- DEPARTAMENTO, MUNICIPIO y DEPARTAMENTAL: categorias textuales que deben validarse contra catalogos y normalizarse.

## Estrategia de limpieza propuesta

### 1. CODIGO

1. Validar que siga el patron `##-##-####-##`.
2. Conservarlo como texto, no como numero.
3. Detectar codigos incompletos o con formato invalido.

### 2. DISTRITO

1. Convertir a texto limpio.
2. Eliminar espacios al inicio y al final.
3. Revisar codigos truncados como `01-` o codigos vacios.
4. Validar que el formato sea consistente con el catalogo del conjunto.

### 3. DEPARTAMENTO, MUNICIPIO y DEPARTAMENTAL

1. Pasar a mayusculas uniformes.
2. Eliminar espacios multiples.
3. Normalizar tildes y variantes de escritura sin cambiar el nombre correcto.
4. Comparar contra el catalogo oficial para detectar valores invalidos.
5. Revisar casos como `CIUDAD CAPITAL` y municipios escritos como zonas urbanas.

### 4. ESTABLECIMIENTO

1. Mantener la ortografia correcta del nombre.
2. Normalizar mayusculas, espacios dobles y caracteres invisibles.
3. Quitar comillas innecesarias alrededor del texto.
4. Revisar variantes de un mismo establecimiento que difieren solo por acentos, signos o espacios.
5. No modificar el nombre por criterio propio; solo corregir forma y consistencia.

### 5. DIRECCION

1. Normalizar espacios y puntuacion.
2. Eliminar caracteres invisibles.
3. Homogeneizar abreviaturas cuando no cambien el sentido.
4. Verificar que no queden direcciones vacias o placeholders.

### 6. TELEFONO

1. Eliminar espacios, guiones y otros separadores no uniformes.
2. Separar o marcar telefonos multiples cuando aparezcan en una sola celda.
3. Detectar telefonos con letras o longitud invalida.
4. Conservar el telefono como texto.

### 7. SUPERVISOR y DIRECTOR

1. Normalizar espacios, mayusculas y tildes.
2. Detectar placeholders como `SIN DATO`, `---` o celdas vacias.
3. Revisar nombres con diferencias ortograficas obvias.

### 8. NIVEL, SECTOR, AREA, STATUS, MODALIDAD, JORNADA y PLAN

1. Revisar que las categorias pertenezcan a un dominio permitido.
2. Unificar variantes escritas de forma distinta pero equivalentes.
3. Documentar cualquier recodificacion y justificarla.

## Reparto de trabajo

### Angel

1. Revisar y documentar el diagnostico inicial del conjunto de datos.
2. Armar las tablas de calidad: faltantes, duplicados, valores invalidos y categorias inconsistentes.
3. Validar contra catalogos de departamentos y municipios.
4. Apoyar la redaccion del plan de limpieza por variable.
5. Usar la base de Roberto para redactar, el Libro de Codigos (descripcion, tipo de dato, dominio, valores posibles, tratamiento aplicado, variables derivadas, fecha de extraccion, fuente y version del conjunto limpio). Recomendado trabajarlo en Google Docs (formato que pide la guia) y exportarlo luego a PDF. **Pendiente** — ver seccion de insumos mas abajo.

### Roberto

1. DONE Ejecutar y mantener el proceso reproducible de conversion de `.xls` a `.csv`.
2. DONE Revisar la limpieza de texto en columnas descriptivas.
3. DONE Estandarizar `TELEFONO`, `CODIGO` y columnas categoricas.
4. DONE Generar el conjunto consolidado limpio y documentar las transformaciones aplicadas en la tabla de registro (Variable, Problema, Transformacion, Registros afectados, Justificacion).
5. DONE Detectar duplicados parciales usando similitud de cadenas (RapidFuzz) sobre ESTABLECIMIENTO, con direccion/telefono como evidencia de apoyo, documentando la decision en vez de fusionar automaticamente.
6. DONE Implementar las pruebas automaticas de validacion del conjunto limpio (15 pruebas con pytest, todas pasando).
7. DONE Generar la tabla comparativa antes/despues del informe de calidad con datos extraidos por codigo.

## Resultados de la limpieza (Roberto, items 2-7)

Codigo en el paquete `limpieza/` (`catalogos.py`, `texto.py`, `telefono.py`, `columnas.py`, `duplicados.py`), orquestado por `limpieza_establecimientos.py` y validado por `test_limpieza.py` (15/15 pruebas OK). Entorno reproducible en `.venv/` + `requirements.txt`.

### Informe de calidad: antes vs. despues

| Metrica | Antes | Despues |
|---|---|---|
| Registros | 11,867 | 11,867 |
| Variables | 17 | 24 (7 derivadas, ver abajo) |
| Valores faltantes (vacios + placeholders) | 4,263 | 4,286 |
| % faltantes | 2.11% | 2.12% |
| Variables con al menos un faltante | 6 | 6 |
| Duplicados exactos (fila completa) | 0 | 0 |
| Posibles duplicados parciales (nombre similar, no identico) | 3,726 | 2,075 |
| Establecimientos unicos (texto) | 6,313 | 5,833 |

El % de faltantes casi no cambia (sube ligeramente): la limpieza no "esconde" datos, los hace **consistentes** (antes convivian vacios, `---`, `.`, `SIN DATO`, `SIN REGISTRO`, etc.; ahora todos son `NA` real y se detectan con una sola regla). El numero real de duplicados parciales candidatos a revision cae de 3,726 a 2,075 porque unificar tildes/puntuacion/comillas antes de comparar elimina falsos positivos causados solo por formato.

### Variables derivadas agregadas (para el Libro de Codigos)

- `DISTRITO_FORMATO` / `DISTRITO_VALIDO`: en el crudo conviven dos esquemas validos de codigo de distrito (`##-###` y `##-##-####`) mas casos vacios/truncados (`01-`); estas columnas documentan cual esquema tiene cada registro en vez de forzar un formato unico.
- `MUNICIPIO_VALIDO`: resultado de comparar `MUNICIPIO` contra un catalogo oficial de departamentos/municipios (fuente: INE/Wikipedia, verificado contra los datos reales). Solo 3 combinaciones quedan fuera de catalogo en las 11,867 filas — ver "Hallazgos" abajo.
- `TELEFONO_ORIGINAL`: valor crudo sin tocar, para poder auditar cualquier numero reconstruido.
- `TELEFONO_CANTIDAD`, `TELEFONO_VALIDO`, `TELEFONO_OBSERVACION`: cuantos telefonos habia en la celda, si son formato moderno de 8 digitos, y notas (FAX, extension, rango no expandido, formato antiguo de 7 digitos).

### Hallazgos que vale la pena que Angel conozca

1. **Sin corrupcion de codificacion**: un caracter `�` visto al inspeccionar `PLAN` resulto ser un artefacto de como la terminal renderiza UTF-8 en Windows, no un problema del dato (se verifico byte a byte). No hace falta re-exportar los `.xls`.
2. **`DEPARTAMENTO` sin tildes**: los 22 departamentos + `CIUDAD CAPITAL` estaban en mayusculas pero sin tilde (`PETEN`, `QUICHE`, `SOLOLA`, etc.), mientras que `DEPARTAMENTAL` (misma fuente) si trae tilde para los mismos lugares. Se normalizo hacia la ortografia correcta.
3. **`CIUDAD CAPITAL` no es un departamento oficial**: es una particion propia de MINEDUC sobre el municipio de Guatemala, reportada por zona (`ZONA 1`..`ZONA 25`) en vez de por municipio. Se documenta como caso especial, no se fuerza dentro de "Guatemala".
4. **`DEPARTAMENTAL` reparte Guatemala en 4 y Quiche en 2**: se verifico por codigo que `GUATEMALA NORTE/SUR/ORIENTE/OCCIDENTE` cubre exactamente las filas de `DEPARTAMENTO` en (`GUATEMALA`, `CIUDAD CAPITAL`), y que `QUICHÉ NORTE` cubre un subconjunto de `DEPARTAMENTO = QUICHÉ`. Sin inconsistencias.
5. **3 municipios que no calzan con ningun alias razonable** (quedan marcados invalidos, no corregidos): `QUEZALTEPEQUE` en Chiquimula (falta la T de "Quetzaltepeque", 30 filas), `PACHALUN` en Quiche (vs. oficial "Pachalum", 18 filas), `SAN MIGUEL PANAM` en Suchitepequez (vs. oficial "San Miguel Panan", 1 fila). Los tres cambian la ultima letra por N — puede ser un patron del sistema fuente de MINEDUC, pero se dejo para que alguien decida en vez de adivinar.
6. **`TELEFONO` es mas complejo de lo que parecia**: ademas de separadores mixtos, hay un patron real de "sufijo abreviado" (`22202870-73` = telefonos 22202870 y 22202873, comparten prefijo) que se reconstruye y se deja documentado; casos con `FAX`, `EXT`/`ESTX` y rangos (`23335736 AL 40`) se marcan pero no se inventan.
7. **"Duplicados" de nombre identico casi siempre NO son error**: 2,372 grupos de establecimientos con el mismo nombre en el mismo municipio son, en su mayoria, la misma escuela con varias filas (una por jornada/plan, o por cambio de `STATUS` en el tiempo). Se separaron en `reportes/establecimientos_nombre_repetido.csv` (con bandera de "direccion distinta" para priorizar revision) para no mezclarlos con los candidatos reales de error ortografico en `reportes/posibles_duplicados_parciales.csv` (2,075 pares, ej. "PREUNIVERSITARIA" vs "PRE-UNIVERSITARIA").

### Que falta (fuera del alcance de Roberto en este avance)

- **Libro de Codigos** (item 8, conjunto con Angel): transcribir la tabla de variables originales + las 7 derivadas de arriba a Google Docs/markdown, con fecha de extraccion, fuente y version.
- **Decision manual sobre los 2,075 pares de `posibles_duplicados_parciales.csv`** y los 3 municipios invalidos documentados arriba: cual se corrige, cual se conserva, y por que (pedido explicito de la guia: no fusionar/eliminar automaticamente).
- **Diagnostico inicial formal de Angel** (valores unicos, tipos de dato, formatos inconsistentes por variable) puede apoyarse en `reportes/informe_calidad_antes_despues.csv` y `reportes/registro_transformaciones.csv`, que ya traen varias de estas metricas calculadas.

## Nota tecnica

La conversion de `.xls` a `.csv` se reproduce con `procesar_establecimientos.py`. La limpieza completa se reproduce con:

```
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt
.venv/Scripts/python limpieza_establecimientos.py   # genera el CSV limpio y los reportes
.venv/Scripts/python -m pytest test_limpieza.py -v  # valida el resultado
```

Salidas: `Datos/csv/establecimientos_diversificado_limpio.csv` (24 columnas, 11,867 filas) y 4 reportes en `reportes/` (registro de transformaciones, informe antes/despues, duplicados parciales, nombres repetidos).