"""Deteccion de duplicados exactos y parciales.

Los duplicados parciales solo se listan para revision manual (no se
fusionan/eliminan automaticamente, por pedido explicito de la guia). Se usa
"blocking" por DEPARTAMENTO+MUNICIPIO para que comparar 11,867 registros sea
viable.
"""

from __future__ import annotations

import pandas as pd
from rapidfuzz import fuzz, process


def detectar_duplicados_exactos(df: pd.DataFrame) -> pd.Series:
    return df.duplicated(keep=False)


def detectar_duplicados_parciales(
    df: pd.DataFrame,
    columna_nombre: str = "ESTABLECIMIENTO",
    columna_bloque: tuple[str, str] = ("DEPARTAMENTO", "MUNICIPIO"),
    umbral: float = 90.0,
) -> pd.DataFrame:
    pares = []
    col_dep, col_mun = columna_bloque
    for (_, _), grupo in df.groupby([col_dep, col_mun]):
        if len(grupo) < 2:
            continue
        nombres = grupo[columna_nombre].tolist()
        indices = grupo.index.tolist()
        matriz = process.cdist(nombres, nombres, scorer=fuzz.token_sort_ratio)
        n = len(nombres)
        for i in range(n):
            for j in range(i + 1, n):
                similitud = matriz[i, j]
                if similitud >= umbral:
                    fila_a, fila_b = grupo.iloc[i], grupo.iloc[j]
                    pares.append(
                        {
                            "indice_a": indices[i],
                            "indice_b": indices[j],
                            "codigo_a": fila_a["CODIGO"],
                            "codigo_b": fila_b["CODIGO"],
                            "establecimiento_a": fila_a[columna_nombre],
                            "establecimiento_b": fila_b[columna_nombre],
                            "similitud_nombre": round(float(similitud), 1),
                            "misma_direccion": fila_a.get("DIRECCION") == fila_b.get("DIRECCION"),
                            "mismo_telefono": fila_a.get("TELEFONO") == fila_b.get("TELEFONO")
                            and fila_a.get("TELEFONO", "") != "",
                            "status_a": fila_a.get("STATUS"),
                            "status_b": fila_b.get("STATUS"),
                            "decision": "pendiente de revision manual",
                        }
                    )
    columnas = [
        "indice_a", "indice_b", "codigo_a", "codigo_b",
        "establecimiento_a", "establecimiento_b", "similitud_nombre",
        "misma_direccion", "mismo_telefono", "status_a", "status_b", "decision",
    ]
    resultado = pd.DataFrame(pares, columns=columnas)
    return resultado.sort_values("similitud_nombre", ascending=False).reset_index(drop=True)


def resumir_nombres_repetidos(
    df: pd.DataFrame,
    columna_nombre: str = "ESTABLECIMIENTO",
    columna_bloque: tuple[str, str] = ("DEPARTAMENTO", "MUNICIPIO"),
) -> pd.DataFrame:
    """Cuando el mismo nombre de establecimiento aparece varias veces en el
    mismo municipio, casi siempre es porque MINEDUC registra un renglon por
    cada combinacion de jornada/plan/sector (o por cambios de STATUS a lo
    largo del tiempo), no porque el dato este duplicado por error. Esta
    tabla resume esos grupos para que la revision manual se enfoque en los
    casos con distinta direccion (mas sospechosos) y no en los miles de
    filas con nombre 100% identico que ya tienen explicacion."""
    col_dep, col_mun = columna_bloque
    filas = []
    for (departamento, municipio, nombre), grupo in df.groupby([col_dep, col_mun, columna_nombre]):
        if len(grupo) < 2:
            continue
        filas.append(
            {
                "departamento": departamento,
                "municipio": municipio,
                "establecimiento": nombre,
                "registros": len(grupo),
                "direcciones_distintas": grupo["DIRECCION"].nunique(),
                "status_distintos": grupo["STATUS"].nunique(),
                "jornadas_distintas": grupo["JORNADA"].nunique(),
                "planes_distintos": grupo["PLAN"].nunique(),
                "codigos": "; ".join(grupo["CODIGO"]),
            }
        )
    resultado = pd.DataFrame(
        filas,
        columns=[
            "departamento", "municipio", "establecimiento", "registros",
            "direcciones_distintas", "status_distintos", "jornadas_distintas",
            "planes_distintos", "codigos",
        ],
    )
    return resultado.sort_values(
        ["direcciones_distintas", "registros"], ascending=[False, False]
    ).reset_index(drop=True)
