"""Normalizacion de la columna TELEFONO.

El guion es ambiguo (formato interno de un numero, separador entre varios
numeros, o sufijo abreviado que comparte prefijo con el numero anterior,
ej. "22202870-73" = 22202870 y 22202873) y FAX/EXT/" AL " marcan casos que
no se deben leer como una linea normal. Detalle completo y riesgos en
avance_proyecto_1.md. El valor crudo se conserva en TELEFONO_ORIGINAL para
poder auditar cualquier numero reconstruido.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

import pandas as pd

from .texto import normalizar_espacios

_MARCA_FAX = re.compile(r"\bFAX\b", re.IGNORECASE)
_MARCA_EXT = re.compile(r"\bEST[XA]?\.?\b|\bEXT\.?\b", re.IGNORECASE)
_MARCA_RANGO = re.compile(r"\bAL\b", re.IGNORECASE)
_SEPARADOR_COARSE = re.compile(r"\s*(?:,|/|\bY\b)\s*", re.IGNORECASE)


@dataclass
class TelefonoParseado:
    numeros: list[str] = field(default_factory=list)
    tiene_fax: bool = False
    tiene_extension: bool = False
    tiene_rango_no_expandido: bool = False
    longitudes_invalidas: list[str] = field(default_factory=list)


def _dividir_token_con_guiones(token: str) -> list[str]:
    partes = token.split("-")
    partes = [p for p in partes if p != ""]
    if len(partes) <= 1:
        return partes

    largas = [p for p in partes if len(p) >= 6]
    if len(largas) == len(partes):
        # Todas las partes ya son numeros completos (8-8, 7-7, 8-7, etc.)
        return partes

    # Primer trozo es el numero de referencia; los siguientes son sufijos
    # cortos que comparten su prefijo, o un formato interno tipo XXX-XXXX.
    primero, resto = partes[0], partes[1:]
    if len(resto) == 1 and len(primero) + len(resto[0]) in (7, 8) and len(primero) in (3, 4):
        # Formato interno de un solo numero, ej. "999-9999" o "9999-9999"
        return [primero + resto[0]]

    resultado = [primero]
    for parte in resto:
        if len(parte) >= 6:
            resultado.append(parte)
        else:
            prefijo = primero[: len(primero) - len(parte)]
            resultado.append(prefijo + parte)
    return resultado


def parsear_telefono(valor: str) -> TelefonoParseado:
    resultado = TelefonoParseado()
    texto = normalizar_espacios(valor)
    if texto == "":
        return resultado

    if _MARCA_RANGO.search(texto):
        resultado.tiene_rango_no_expandido = True
        return resultado

    if _MARCA_FAX.search(texto):
        resultado.tiene_fax = True
        texto = _MARCA_FAX.split(texto)[0]
    if _MARCA_EXT.search(texto):
        resultado.tiene_extension = True
        texto = _MARCA_EXT.split(texto)[0]

    texto = normalizar_espacios(texto)
    if texto == "":
        return resultado

    tokens_gruesos = [t for t in _SEPARADOR_COARSE.split(texto) if t.strip()]
    numeros: list[str] = []
    for token in tokens_gruesos:
        token = token.strip()
        if not re.fullmatch(r"[\d\- ]+", token):
            # Quedo texto no reconocido (abreviaturas no previstas); se marca
            # como longitud invalida en vez de intentar adivinar su forma.
            resultado.longitudes_invalidas.append(token)
            continue
        for sub in token.split():
            for numero in _dividir_token_con_guiones(sub):
                digitos = re.sub(r"\D", "", numero)
                if digitos == "":
                    continue
                if len(digitos) in (7, 8):
                    numeros.append(digitos)
                else:
                    resultado.longitudes_invalidas.append(digitos)

    resultado.numeros = numeros
    return resultado


def formato_valido(parseado: TelefonoParseado) -> bool:
    if not parseado.numeros:
        return False
    if parseado.longitudes_invalidas or parseado.tiene_rango_no_expandido:
        return False
    return all(len(n) == 8 for n in parseado.numeros)


def observacion(parseado: TelefonoParseado, original: str) -> str:
    if normalizar_espacios(original) == "":
        return "vacio"
    notas = []
    if parseado.tiene_rango_no_expandido:
        notas.append("rango no expandido (revision manual)")
    if parseado.tiene_fax:
        notas.append("incluye FAX")
    if parseado.tiene_extension:
        notas.append("incluye extension")
    if parseado.longitudes_invalidas:
        notas.append(f"longitud invalida: {', '.join(parseado.longitudes_invalidas)}")
    if any(len(n) == 7 for n in parseado.numeros):
        notas.append("formato antiguo de 7 digitos")
    if len(parseado.numeros) > 1:
        notas.append(f"{len(parseado.numeros)} telefonos en una celda")
    return "; ".join(notas) if notas else "ok"


def procesar_telefono(valores: list[str]) -> dict[str, list]:
    limpio, cantidad, valido, obs = [], [], [], []
    for original in valores:
        parseado = parsear_telefono(original)
        limpio.append("; ".join(parseado.numeros) if parseado.numeros else pd.NA)
        cantidad.append(len(parseado.numeros))
        valido.append(formato_valido(parseado))
        obs.append(observacion(parseado, original))
    return {
        "TELEFONO": limpio,
        "TELEFONO_CANTIDAD": cantidad,
        "TELEFONO_VALIDO": valido,
        "TELEFONO_OBSERVACION": obs,
    }
