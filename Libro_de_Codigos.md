# Libro de Códigos (Code Book)
**Proyecto 1 - Obtención y Limpieza de Datos - Data Science**

## Metadatos del Conjunto de Datos Limpio
- **Fecha de extracción:** 19 de julio de 2026 *(Fecha correspondiente a la corrida del script de descarga)*
- **Fuente de los datos:** Portal web del Ministerio de Educación de Guatemala (MINEDUC) - Búsqueda de Establecimientos (http://www.mineduc.gob.gt/BUSCAESTABLECIMIENTO_GE/).
- **Versión del conjunto limpio:** 1.0 (Julio 2026)

---

## Diccionario de Variables

### 1. CODIGO
*   **Descripción:** Identificador único del establecimiento educativo asignado por el MINEDUC.
*   **Tipo de dato:** Alfanumérico (Texto).
*   **Dominio permitido:** Cadena de caracteres que cumpla estrictamente con el patrón `##-##-####-##` (dígitos y guiones).
*   **Valores posibles:** Múltiples códigos únicos, ej. `16-01-0137-46`.
*   **Tratamiento aplicado:** Se verificó el patrón regex en el 100% de los registros. Se conservó como texto para no perder ceros a la izquierda y guiones. Normalización de espacios.
*   **Variables derivadas:** Ninguna.

### 2. DISTRITO
*   **Descripción:** Código del distrito escolar al que pertenece el establecimiento.
*   **Tipo de dato:** Alfanumérico (Texto).
*   **Dominio permitido:** Patrones `##-##-####` (detallado) o `##-###` (corto). 
*   **Valores posibles:** Ej. `16-006`, `01-01-0001`, `NA` (si no existe dato).
*   **Tratamiento aplicado:** Normalización de espacios. Los valores truncados o vacíos evidentes (ej. `01-` sin el código completo) se asignaron a `NA`.
*   **Variables derivadas:** 
    *   `DISTRITO_FORMATO`: (Categórico) Indica si el formato es 'detallado', 'corto', 'incompleto', 'vacio' o 'formato_no_reconocido'.
    *   `DISTRITO_VALIDO`: (Booleano) `True` si cumple formatos aceptados, `False` en incompletos o vacíos.

### 3. DEPARTAMENTO
*   **Descripción:** Nombre del departamento político-administrativo donde se ubica el centro educativo.
*   **Tipo de dato:** Texto categórico.
*   **Dominio permitido:** Los 22 departamentos oficiales de la República de Guatemala, más la partición "CIUDAD CAPITAL".
*   **Valores posibles:** ALTA VERAPAZ, BAJA VERAPAZ, CIUDAD CAPITAL, GUATEMALA, PETÉN, QUICHÉ, SACATEPÉQUEZ, SOLOLÁ, etc.
*   **Tratamiento aplicado:** Se convirtieron los textos a mayúsculas, se limpiaron espacios y se corrigieron tildes faltantes usando un catálogo estándar de departamentos (Ej. PETEN -> PETÉN).
*   **Variables derivadas:** Ninguna.

### 4. MUNICIPIO
*   **Descripción:** Nombre del municipio donde se ubica el establecimiento. En el caso de "CIUDAD CAPITAL", reporta la zona.
*   **Tipo de dato:** Texto categórico.
*   **Dominio permitido:** Catálogo oficial del INE/Wikipedia por departamento, y de `ZONA 1` a `ZONA 25` para Ciudad Capital.
*   **Valores posibles:** COBÁN, MIXCO, ZONA 10, etc.
*   **Tratamiento aplicado:** Transformación a mayúsculas, normalización de espacios y corrección de tildes según diccionario municipal.
*   **Variables derivadas:**
    *   `MUNICIPIO_VALIDO`: (Booleano) `True` si el municipio hace match exacto con el diccionario oficial del INE/Wikipedia para su departamento correspondiente, `False` de lo contrario.

### 5. ESTABLECIMIENTO
*   **Descripción:** Nombre oficial del centro educativo.
*   **Tipo de dato:** Texto libre.
*   **Dominio permitido:** Nombres en mayúsculas, letras, números y signos de puntuación válidos.
*   **Valores posibles:** Múltiples (ej. INSTITUTO MIXTO NOCTURNO FRANCISCO MARROQUIN).
*   **Tratamiento aplicado:** Eliminación de caracteres invisibles, normalización de múltiples espacios internos y reemplazo de acentos graves por agudos. Se eliminaron comillas dobles si envolvían toda la cadena. Valores vacíos explícitos se pasaron a `NA`. Unificación por similitud estricta (tildes).
*   **Variables derivadas:** Ninguna.

### 6. DIRECCION
*   **Descripción:** Dirección física de las instalaciones del establecimiento.
*   **Tipo de dato:** Texto libre.
*   **Dominio permitido:** Direcciones (alfanumérico). `NA` si es placeholder.
*   **Valores posibles:** Múltiples (ej. "6A. AVENIDA 1-15 ZONA 4").
*   **Tratamiento aplicado:** Eliminación de espacios invisibles/múltiples, eliminación de signos de puntuación irregulares en los bordes. Reemplazo de placeholders ("SIN DATO", "---", etc.) por `NA`.
*   **Variables derivadas:** Ninguna.

### 7. TELEFONO
*   **Descripción:** Números de teléfono de contacto del establecimiento.
*   **Tipo de dato:** Texto (lista de números separados por punto y coma `;`).
*   **Dominio permitido:** Dígitos de 8 caracteres separados por `;`. `NA` si es faltante/inválido.
*   **Valores posibles:** Ej. `22202870`, `22202870; 22202873`.
*   **Tratamiento aplicado:** Se estandarizaron separadores (comas, "Y", "/"). Se reconstruyeron números abreviados (ej. `22202870-73` a `22202870; 22202873`). Se eliminaron etiquetas como "FAX" y "EXT". Los caracteres imposibles se documentaron en observación.
*   **Variables derivadas:** 
    *   `TELEFONO_ORIGINAL`: (Texto) El valor crudo para trazabilidad y auditoría.
    *   `TELEFONO_CANTIDAD`: (Numérico entero) Cantidad de números extraídos exitosamente.
    *   `TELEFONO_VALIDO`: (Booleano) `True` si todos los números extraídos tienen longitud válida (8 dígitos).
    *   `TELEFONO_OBSERVACION`: (Texto libre) Motivos de invalidez o notas de extracción (ej. "incluye FAX", "vacio", "longitud invalida").

### 8. SUPERVISOR
*   **Descripción:** Nombre de la persona encargada de la supervisión escolar del MINEDUC asignada.
*   **Tipo de dato:** Texto libre.
*   **Dominio permitido:** Cadenas de nombres propios, `NA` si falta.
*   **Valores posibles:** Múltiples (ej. JORGE EDUARDO PAQUE LAZARO).
*   **Tratamiento aplicado:** Eliminación de múltiples espacios y caracteres invisibles. Corrección de acentos graves. Reemplazo de placeholders ("---", "S/D") a `NA`. Unificación automática de nombres idénticos que solo diferían por tildes.
*   **Variables derivadas:** Ninguna.

### 9. DIRECTOR
*   **Descripción:** Nombre del director del centro educativo.
*   **Tipo de dato:** Texto libre.
*   **Dominio permitido:** Cadenas de nombres propios, `NA` si falta.
*   **Valores posibles:** Múltiples nombres de personas.
*   **Tratamiento aplicado:** Normalización completa (espacios, caracteres invisibles, corrección de acentos graves). Conversión de valores vacíos y placeholders genéricos ("---", "SIN DATO", ".") a valor nulo explícito `NA`. Unificación por presencia de tildes.
*   **Variables derivadas:** Ninguna.

### 10. NIVEL
*   **Descripción:** Nivel educativo de los datos extraídos (condición del proyecto).
*   **Tipo de dato:** Texto categórico.
*   **Dominio permitido:** "DIVERSIFICADO"
*   **Valores posibles:** DIVERSIFICADO
*   **Tratamiento aplicado:** Normalización de espacios y mayúsculas para estandarización.
*   **Variables derivadas:** Ninguna.

### 11. SECTOR
*   **Descripción:** Naturaleza jurídica / administración financiera del establecimiento.
*   **Tipo de dato:** Texto categórico.
*   **Dominio permitido:** Lista controlada según sistema (ej. PRIVADO, OFICIAL, COOPERATIVA).
*   **Valores posibles:** PRIVADO, OFICIAL, MUNICIPAL, COOPERATIVA.
*   **Tratamiento aplicado:** Normalización de espacios y conversión a mayúsculas.
*   **Variables derivadas:** Ninguna.

### 12. AREA
*   **Descripción:** Tipo de área demográfica de asentamiento de la escuela.
*   **Tipo de dato:** Texto categórico.
*   **Dominio permitido:** URBANA, RURAL (y SIN ESPECIFICAR por consistencia de origen).
*   **Valores posibles:** URBANA, RURAL, SIN ESPECIFICAR.
*   **Tratamiento aplicado:** Normalización de espacios y mayúsculas.
*   **Variables derivadas:** Ninguna.

### 13. STATUS
*   **Descripción:** Situación operativa actual del establecimiento.
*   **Tipo de dato:** Texto categórico.
*   **Dominio permitido:** Estados operacionales del MINEDUC.
*   **Valores posibles:** ABIERTA, CERRADA TEMPORALMENTE, CERRADA DEFINITIVAMENTE.
*   **Tratamiento aplicado:** Limpieza de espacios y estandarización a mayúsculas.
*   **Variables derivadas:** Ninguna.

### 14. MODALIDAD
*   **Descripción:** Idioma y enfoque educativo.
*   **Tipo de dato:** Texto categórico.
*   **Dominio permitido:** Modalidades lingüísticas reconocidas.
*   **Valores posibles:** MONOLINGUE, BILINGUE.
*   **Tratamiento aplicado:** Normalización de espacios, estandarización a mayúsculas.
*   **Variables derivadas:** Ninguna.

### 15. JORNADA
*   **Descripción:** Horario de funcionamiento de clases.
*   **Tipo de dato:** Texto categórico.
*   **Dominio permitido:** Jornadas del MINEDUC.
*   **Valores posibles:** MATUTINA, VESPERTINA, NOCTURNA, DOBLE, INTERMEDIA.
*   **Tratamiento aplicado:** Estandarización a mayúsculas, recortes de espacio.
*   **Variables derivadas:** Ninguna.

### 16. PLAN
*   **Descripción:** Plan o tipo de asistencia escolar.
*   **Tipo de dato:** Texto categórico.
*   **Dominio permitido:** Planes educativos del MINEDUC.
*   **Valores posibles:** DIARIO(REGULAR), FIN DE SEMANA, SEMIPRESENCIAL, A DISTANCIA.
*   **Tratamiento aplicado:** Remoción de espacios extra y conversión a formato uniforme.
*   **Variables derivadas:** Ninguna.

### 17. DEPARTAMENTAL
*   **Descripción:** Entidad Departamental del MINEDUC encargada de la administración sobre el establecimiento.
*   **Tipo de dato:** Texto categórico.
*   **Dominio permitido:** Departamentos, con subdivisiones de GUATEMALA y QUICHÉ (Norte, Sur, Oriente, Occidente).
*   **Valores posibles:** ALTA VERAPAZ, GUATEMALA NORTE, QUICHÉ NORTE, etc.
*   **Tratamiento aplicado:** Conversión a mayúsculas, adición de tildes oficiales en concordancia con `DEPARTAMENTO` (Ej. QUICHÉ). Validado respecto al departamento base para asegurar congruencia jerárquica territorial.
*   **Variables derivadas:** Ninguna.

---

## Informe de Calidad de Datos (Antes vs. Después)

A continuación, se presenta la validación del conjunto de datos limpio comparando el estado inicial contra el final tras aplicar el proceso de normalización:

| Métrica | Antes | Después | Justificación de cambios |
| :--- | :--- | :--- | :--- |
| **Registros** | 11,867 | 11,867 | No se eliminaron registros, el sistema de MINEDUC asocia un registro distinto por combinación jornada/plan. |
| **Variables (columnas)** | 17 | 24 | Se agregaron 7 columnas derivadas para validación explícita (DISTRITO_FORMATO, DISTRITO_VALIDO, MUNICIPIO_VALIDO, TELEFONO_ORIGINAL, TELEFONO_CANTIDAD, TELEFONO_VALIDO, TELEFONO_OBSERVACION). |
| **Valores faltantes** | 4,263 | 4,286 | Subida esperada. Placeholders tipo "---", "SIN DATOS" o "S/D" fueron convertidos a nulos explícitos (NA) para mediciones reales. |
| **% de faltantes** | 2.11% | 2.12% | Aumento derivado de la conversión de texto genérico a NA. |
| **Variables con NA** | 6 | 6 | Las variables que contienen datos nulos se mantuvieron estables (Director, Supervisor, Dirección, etc). |
| **Duplicados exactos (fila completa)** | 0 | 0 | No existían filas 100% idénticas en todas sus columnas en el origen. |
| **Posibles duplicados parciales** | 3,726 | 2,075 | Se redujeron drásticamente las discrepancias parciales (similitud difusa) gracias a la corrección estandarizada de tildes en nombres propios. |
| **Establecimientos únicos** | 6,313 | 5,833 | Al corregir variaciones ortográficas (ej. GONZÁLEZ vs GONZALEZ), entidades lógicamente idénticas se unificaron, reduciendo el total. |

*Nota: Todas las transformaciones aplicadas fueron guardadas para reproducibilidad en `Reportes/RegistroTransformaciones.csv`. Los duplicados parciales restantes se exportaron a `Reportes/PosiblesDuplicadosParciales.csv` para revisión manual del analista, de acuerdo con las instrucciones del proyecto que prohíben su eliminación automática.*