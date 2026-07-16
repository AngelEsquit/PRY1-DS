"""Pruebas automaticas de validacion del conjunto limpio (item 7 de la guia).

Ejecutar con: .venv/Scripts/python.exe -m pytest test_limpieza.py -v

Estas pruebas corren sobre el CSV ya exportado por limpieza_establecimientos.py
(no vuelven a correr la limpieza) para verificar que el ENTREGABLE final
cumple las reglas de calidad pedidas.
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
import pytest

from limpieza import catalogos

ROOT = Path(__file__).resolve().parent
CSV_LIMPIO = ROOT / "Datos/csv/establecimientos_diversificado_limpio.csv"

COLUMNAS_ORIGINALES = [
    "CODIGO", "DISTRITO", "DEPARTAMENTO", "MUNICIPIO", "ESTABLECIMIENTO",
    "DIRECCION", "TELEFONO", "SUPERVISOR", "DIRECTOR", "NIVEL", "SECTOR",
    "AREA", "STATUS", "MODALIDAD", "JORNADA", "PLAN", "DEPARTAMENTAL",
]
COLUMNAS_TEXTO_LIBRE = [
    "ESTABLECIMIENTO", "DIRECCION", "SUPERVISOR", "DIRECTOR",
]
COLUMNAS_CATEGORICAS = [
    "DEPARTAMENTO", "SECTOR", "AREA", "STATUS", "MODALIDAD", "JORNADA",
    "PLAN", "DEPARTAMENTAL", "NIVEL",
]

# Los unicos valores de MUNICIPIO fuera de catalogo que se aceptan sin fallar
# la prueba son los documentados explicitamente en el informe de calidad
# (ver limpieza/catalogos.py): variantes ortograficas de la fuente MINEDUC
# que se dejaron para revision manual en vez de corregirse por adivinanza.
MUNICIPIOS_INVALIDOS_DOCUMENTADOS = {
    ("CHIQUIMULA", "QUEZALTEPEQUE"),
    ("QUICHÉ", "PACHALUN"),
    ("SUCHITEPÉQUEZ", "SAN MIGUEL PANAM"),
}


@pytest.fixture(scope="module")
def df() -> pd.DataFrame:
    if not CSV_LIMPIO.exists():
        pytest.skip("Corra limpieza_establecimientos.py antes de las pruebas.")
    return pd.read_csv(CSV_LIMPIO, dtype=str, keep_default_na=True, encoding="utf-8")


def test_no_hay_duplicados_exactos(df):
    assert df[COLUMNAS_ORIGINALES].duplicated().sum() == 0


def test_no_hay_espacios_al_inicio_o_final(df):
    for col in COLUMNAS_ORIGINALES:
        valores = df[col].dropna()
        con_espacio_borde = valores[valores != valores.str.strip()]
        assert con_espacio_borde.empty, f"{col} tiene {len(con_espacio_borde)} valores con espacios en el borde"


def test_no_hay_espacios_multiples_internos(df):
    patron = re.compile(r" {2,}")
    for col in COLUMNAS_ORIGINALES:
        valores = df[col].dropna()
        con_espacio_doble = valores[valores.str.contains(patron)]
        assert con_espacio_doble.empty, f"{col} tiene {len(con_espacio_doble)} valores con espacios dobles"


def test_telefono_formato_consistente(df):
    """TELEFONO debe ser NA o una lista de grupos de 7-8 digitos separados
    por '; '. La validez semantica (si el numero es completo/moderno) se
    verifica aparte en TELEFONO_VALIDO; aqui solo se valida la FORMA."""
    patron_grupo = re.compile(r"^\d{7,8}$")
    valores = df["TELEFONO"].dropna()
    for valor in valores:
        grupos = valor.split("; ")
        for grupo in grupos:
            assert patron_grupo.match(grupo), f"grupo de telefono con formato inesperado: {grupo!r}"


def test_telefono_valido_es_booleano_y_consistente_con_cantidad(df):
    assert df["TELEFONO_VALIDO"].dropna().isin(["True", "False"]).all() or df["TELEFONO_VALIDO"].dtype == bool
    cantidad = pd.to_numeric(df["TELEFONO_CANTIDAD"])
    sin_numeros = cantidad == 0
    valido = df["TELEFONO_VALIDO"].astype(str) == "True"
    assert not (sin_numeros & valido).any(), "hay filas TELEFONO_VALIDO=True sin ningun numero"


def test_departamento_pertenece_al_catalogo(df):
    invalidos = df.loc[~df["DEPARTAMENTO"].map(catalogos.departamento_valido), "DEPARTAMENTO"].unique()
    assert len(invalidos) == 0, f"departamentos fuera de catalogo: {invalidos}"


def test_municipio_pertenece_al_catalogo_o_esta_documentado(df):
    combinaciones = df.loc[df["MUNICIPIO_VALIDO"].astype(str) == "False", ["DEPARTAMENTO", "MUNICIPIO"]].drop_duplicates()
    no_documentados = [
        tuple(fila) for fila in combinaciones.itertuples(index=False)
        if tuple(fila) not in MUNICIPIOS_INVALIDOS_DOCUMENTADOS
    ]
    assert not no_documentados, f"municipios invalidos sin documentar en el informe: {no_documentados}"


def test_codigo_cumple_patron(df):
    patron = re.compile(r"^\d{2}-\d{2}-\d{4}-\d{2}$")
    assert df["CODIGO"].str.match(patron).all()


def test_codigo_es_unico(df):
    assert df["CODIGO"].is_unique


def test_categorias_sin_duplicados_por_escritura(df):
    """Dentro de cada columna categorica, dos valores distintos no deberian
    normalizar al mismo texto (mayusculas + sin tildes): eso indicaria una
    categoria escrita de dos formas que quedo sin unificar."""
    from unidecode import unidecode

    for col in COLUMNAS_CATEGORICAS:
        valores = df[col].dropna().unique()
        normalizados: dict[str, str] = {}
        conflictos = []
        for valor in valores:
            clave = unidecode(valor).upper()
            if clave in normalizados and normalizados[clave] != valor:
                conflictos.append((normalizados[clave], valor))
            normalizados[clave] = valor
        assert not conflictos, f"{col} tiene categorias duplicadas por escritura: {conflictos}"


def test_columnas_de_bandera_son_booleanas(df):
    for col in ["DISTRITO_VALIDO", "MUNICIPIO_VALIDO", "TELEFONO_VALIDO"]:
        valores = set(df[col].astype(str).unique())
        assert valores <= {"True", "False"}, f"{col} tiene valores no booleanos: {valores}"


def test_placeholders_conocidos_no_quedan_como_texto(df):
    patron_placeholder = re.compile(r"^[-.,_]+$|^[xX0]+$")
    literales = {"N/A", "NA", "N.A", "NULL", "NONE", "SIN DATO", "SIN DATOS", "S/D", "SD", "SIN REGISTRO"}
    for col in COLUMNAS_TEXTO_LIBRE:
        valores = df[col].dropna()
        con_placeholder = valores[valores.str.match(patron_placeholder) | valores.str.upper().isin(literales)]
        assert con_placeholder.empty, f"{col} conserva placeholders como texto: {con_placeholder.unique()}"


def test_establecimiento_sin_comillas_envolventes_completas(df):
    valores = df["ESTABLECIMIENTO"].dropna()
    envueltos = valores[valores.str.match(r'^".*"$')]
    assert envueltos.empty, f"ESTABLECIMIENTO con comillas envolviendo todo el nombre: {envueltos.tolist()}"


def test_reportes_generados_existen():
    reportes = ROOT / "reportes"
    for nombre in [
        "registro_transformaciones.csv",
        "informe_calidad_antes_despues.csv",
        "posibles_duplicados_parciales.csv",
        "establecimientos_nombre_repetido.csv",
    ]:
        archivo = reportes / nombre
        assert archivo.exists(), f"falta el reporte {nombre}"
        assert archivo.stat().st_size > 0, f"{nombre} esta vacio"


def test_registro_transformaciones_cubre_las_17_variables():
    tabla = pd.read_csv(ROOT / "reportes/registro_transformaciones.csv", encoding="utf-8")
    variables_cubiertas = set(tabla["Variable"])
    faltantes = set(COLUMNAS_ORIGINALES) - variables_cubiertas
    assert not faltantes, f"variables sin entrada en el registro de transformaciones: {faltantes}"
