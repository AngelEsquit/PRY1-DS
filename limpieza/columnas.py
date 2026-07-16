"""Limpieza especifica por columna (excepto TELEFONO, que vive en telefono.py)."""

from __future__ import annotations

import re

import pandas as pd
from unidecode import unidecode

from . import catalogos
from .texto import es_placeholder_faltante, limpiar_texto_general, normalizar_espacios

PATRON_CODIGO = re.compile(r"^\d{2}-\d{2}-\d{4}-\d{2}$")
PATRON_DISTRITO_DETALLADO = re.compile(r"^\d{2}-\d{2}-\d{4}$")
PATRON_DISTRITO_CORTO = re.compile(r"^\d{2}-\d{3}$")
PATRON_DISTRITO_INCOMPLETO = re.compile(r"^\d{2}-$")


def procesar_codigo(serie: pd.Series) -> tuple[pd.Series, pd.Series]:
    """CODIGO ya cumple el patron ##-##-####-## en el 100% de los registros
    del crudo; se conserva como texto y se devuelve una bandera de validez
    para dejar la verificacion explicita en vez de asumirla."""
    limpio = serie.map(normalizar_espacios)
    valido = limpio.str.match(PATRON_CODIGO)
    return limpio, valido


def clasificar_distrito(valor: str) -> str:
    if valor == "":
        return "vacio"
    if PATRON_DISTRITO_DETALLADO.match(valor):
        return "detallado"
    if PATRON_DISTRITO_CORTO.match(valor):
        return "corto"
    if PATRON_DISTRITO_INCOMPLETO.match(valor):
        return "incompleto"
    return "formato_no_reconocido"


def procesar_distrito(serie: pd.Series) -> tuple[pd.Series, pd.Series, pd.Series]:
    """DISTRITO conviven dos esquemas validos de MINEDUC (##-## y
    ##-##-####); se documentan ambos en vez de forzar uno solo. Los valores
    truncados (##-) o vacios se marcan como invalidos, no se completan."""
    limpio = serie.map(normalizar_espacios)
    clase = limpio.map(clasificar_distrito)
    valido = clase.isin(["detallado", "corto"])
    # Solo se marca NA lo realmente vacio; "incompleto" (ej. "01-") conserva
    # el prefijo de departamento que si trae, y se senala via DISTRITO_VALIDO.
    limpio = limpio.mask(clase == "vacio", pd.NA)
    return limpio, clase, valido


def procesar_departamento(serie: pd.Series) -> tuple[pd.Series, pd.Series]:
    limpio = serie.map(normalizar_espacios).map(catalogos.departamento_canonico)
    valido = serie.map(catalogos.departamento_valido)
    return limpio, valido


def procesar_municipio(departamento: pd.Series, municipio: pd.Series) -> tuple[pd.Series, pd.Series]:
    municipio_limpio = municipio.map(normalizar_espacios)
    limpio = [
        catalogos.municipio_canonico(d, m) for d, m in zip(departamento, municipio_limpio)
    ]
    valido = [
        catalogos.municipio_valido(d, m) for d, m in zip(departamento, municipio_limpio)
    ]
    return pd.Series(limpio, index=municipio.index), pd.Series(valido, index=municipio.index)


def procesar_categorica_simple(serie: pd.Series) -> pd.Series:
    """Para columnas de dominio pequeno que el perfilado ya mostro limpias
    (NIVEL, SECTOR, AREA, STATUS, MODALIDAD, JORNADA, PLAN, DEPARTAMENTAL):
    solo normaliza espacios/mayusculas; no se detectaron variantes de
    escritura para unificar en el crudo."""
    return serie.map(normalizar_espacios).str.upper()


def _variante_mas_correcta(variantes: list[str]) -> str:
    """Entre variantes que solo difieren en tildes (misma palabra sin
    acentos), prefiere la forma con mas vocales acentuadas: el espanol
    requiere la tilde, quitarla es el error, no al reves."""
    return max(variantes, key=lambda v: (sum(1 for c in v if c in "ÁÉÍÓÚ"), v))


def unificar_variantes_por_tilde(serie: pd.Series) -> tuple[pd.Series, dict[str, str]]:
    """Unifica registros que son identicos salvo por tildes (incluye typos
    de acento grave ya corregidos antes de esta funcion): por ejemplo
    'CARLOS HUMBERTO GONZALEZ DE LEON' y 'CARLOS HUMBERTO GONZÁLEZ DE LEÓN'
    en SUPERVISOR, o variantes equivalentes en ESTABLECIMIENTO y DIRECTOR.
    No toca diferencias de letras, orden de palabras o abreviaturas
    distintas: esas quedan para el analisis de duplicados parciales, donde
    cada caso se documenta uno por uno en vez de fusionarse automaticamente.
    Ignora los valores NA (no hay nada que unificar en un dato faltante)."""
    no_nulos = serie.dropna()
    base = no_nulos.map(unidecode)
    grupos = no_nulos.groupby(base).unique()
    mapa: dict[str, str] = {}
    for variantes in grupos:
        if len(variantes) > 1:
            canonico = _variante_mas_correcta(list(variantes))
            for variante in variantes:
                if variante != canonico:
                    mapa[variante] = canonico
    limpio = serie.replace(mapa)
    return limpio, mapa


def procesar_texto_libre_con_placeholder(serie: pd.Series) -> tuple[pd.Series, dict[str, str]]:
    """Para DIRECTOR, SUPERVISOR y DIRECCION: normaliza texto, unifica
    variantes que solo difieren en tildes, y convierte placeholders (---,
    ..., S/D, SIN REGISTRO, vacios) en NA real para que se cuenten como
    faltantes en vez de como texto valido."""
    limpio = serie.map(limpiar_texto_general)
    limpio, mapa_tildes = unificar_variantes_por_tilde(limpio)
    limpio = limpio.mask(limpio.map(es_placeholder_faltante), pd.NA)
    return limpio, mapa_tildes


def procesar_establecimiento(serie: pd.Series) -> tuple[pd.Series, dict[str, str]]:
    limpio = serie.map(limpiar_texto_general)
    limpio, mapa_tildes = unificar_variantes_por_tilde(limpio)
    # No se puede inventar el nombre de un establecimiento: los vacios se
    # marcan NA explicito en vez de quedar como cadena vacia silenciosa.
    limpio = limpio.mask(limpio == "", pd.NA)
    return limpio, mapa_tildes
