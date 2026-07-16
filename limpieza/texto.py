"""Utilidades genericas de normalizacion de texto.

Estas funciones se usan sobre cualquier columna de texto libre. No corrigen
ortografia de nombres propios (eso requeriria criterio editorial que el
proyecto explicitamente prohibe aplicar de forma automatica); solo resuelven
problemas de forma: espacios, caracteres invisibles, comillas envolventes y
un typo comun de tildes.
"""

from __future__ import annotations

import re

# Espacio de no separacion, espacios de ancho variable y caracteres de ancho
# cero que a veces llegan de copiar/pegar desde Excel o Word.
_CARACTERES_INVISIBLES = re.compile(
    "[ ​‌‍⁠﻿\t]"
)
_ESPACIOS_MULTIPLES = re.compile(r" {2,}")
_PUNTUACION_SUELTA_BORDE_INICIO = re.compile(r"^[,;:\s]+")
_PUNTUACION_SUELTA_BORDE_FINAL = re.compile(r"[,;:\s]+$")

# El espanol no usa acento grave; cuando aparece es casi siempre un typo de
# teclado por el acento agudo correcto.
_ACENTOS_GRAVES = str.maketrans("àèìòùÀÈÌÒÙ", "áéíóúÁÉÍÓÚ")

_PLACEHOLDERS_FALTANTE = {
    "N/A", "NA", "N.A", "NULL", "NONE", "SIN DATO", "SIN DATOS", "S/D", "SD",
    "SIN REGISTRO",
}


def normalizar_espacios(valor: str) -> str:
    """Colapsa caracteres invisibles y espacios multiples; recorta bordes."""
    if valor is None:
        return ""
    limpio = _CARACTERES_INVISIBLES.sub(" ", valor)
    limpio = _ESPACIOS_MULTIPLES.sub(" ", limpio)
    return limpio.strip()


def corregir_acentos_graves(valor: str) -> str:
    """Sustituye acentos graves (ausentes en espanol) por su equivalente agudo."""
    return valor.translate(_ACENTOS_GRAVES)


def quitar_comillas_envolventes(valor: str) -> str:
    """Quita comillas dobles solo cuando envuelven la cadena COMPLETA
    (ej. '"LICEO LA SALLE"'). Si las comillas estan alrededor de una sola
    palabra dentro de un nombre mas largo (ej. COLEGIO "LA PATRIA"), se
    conservan porque son parte legitima del nombre del establecimiento."""
    if len(valor) >= 2 and valor.startswith('"') and valor.endswith('"'):
        interior = valor[1:-1]
        if '"' not in interior:
            return interior.strip()
    return valor


def quitar_puntuacion_suelta(valor: str) -> str:
    """Quita comas/puntoycoma/dos puntos sueltos al inicio o final (ej.
    'CATALINA PERALTA CARRILLO,' o '10A. AVENIDA 2-24,'). No toca el punto
    final: en DIRECCION casi siempre es parte de una abreviatura (ej. 'ZONA 4.')."""
    limpio = _PUNTUACION_SUELTA_BORDE_INICIO.sub("", valor)
    limpio = _PUNTUACION_SUELTA_BORDE_FINAL.sub("", limpio)
    return limpio


def limpiar_texto_general(valor: str) -> str:
    """Pipeline estandar para columnas de texto libre: espacios -> tildes
    invalidas -> comillas envolventes -> puntuacion suelta en los bordes."""
    limpio = normalizar_espacios(valor)
    limpio = corregir_acentos_graves(limpio)
    limpio = quitar_comillas_envolventes(limpio)
    limpio = quitar_puntuacion_suelta(limpio)
    return limpio


def es_placeholder_faltante(valor: str) -> bool:
    """Detecta valores que representan 'sin dato' aunque no esten vacios:
    solo puntuacion/guiones repetidos (---, ., ..), solo X/0 repetidos, o
    literales conocidos (N/A, NULL, SIN DATO, S/D)."""
    limpio = valor.strip()
    if limpio == "":
        return True
    if re.fullmatch(r"[-.,_]+", limpio):
        return True
    if re.fullmatch(r"[xX0]+", limpio):
        return True
    if limpio.upper() in _PLACEHOLDERS_FALTANTE:
        return True
    return False
