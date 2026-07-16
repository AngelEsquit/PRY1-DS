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

### Roberto

1. Ejecutar y mantener el proceso reproducible de conversion de `.xls` a `.csv`.
2. Revisar la limpieza de texto en columnas descriptivas.
3. Estandarizar `TELEFONO`, `CODIGO` y columnas categoricas.
4. Generar el conjunto consolidado limpio y documentar las transformaciones aplicadas.

## Nota tecnica

La conversion ya puede reproducirse con el script `procesar_establecimientos.py`. El flujo toma cada `.xls`, identifica la fila de encabezados correcta y exporta un CSV con solo las 17 variables utiles.