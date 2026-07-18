"""Limpieza reproducible del conjunto consolidado de establecimientos educativos.

Lee `Datos/Csv/EstablecimientosDiversificadoConsolidado.csv` (salida de
`ProcesarEstablecimientos.py`), aplica las reglas de limpieza descritas en
`AvanceProyecto1.md` usando los modulos del paquete `Limpieza/`, y exporta:

- Datos/Csv/EstablecimientosDiversificadoLimpio.csv   (dataset limpio)
- Reportes/RegistroTransformaciones.csv               (item 6 de la guia)
- Reportes/InformeCalidadAntesDespues.csv              (item 8 de la guia)
- Reportes/PosiblesDuplicadosParciales.csv             (item 5.g de la guia)

Ejecutar con: .venv/Scripts/python.exe LimpiezaEstablecimientos.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from Limpieza import Catalogos, Columnas, Duplicados
from Limpieza.Telefono import procesar_telefono
from Limpieza.Texto import es_placeholder_faltante

ROOT = Path(__file__).resolve().parent
ENTRADA = ROOT / "Datos/Csv/EstablecimientosDiversificadoConsolidado.csv"
SALIDA_CSV = ROOT / "Datos/Csv/EstablecimientosDiversificadoLimpio.csv"
REPORTES_DIR = ROOT / "Reportes"

COLUMNAS_ORIGINALES = [
    "CODIGO", "DISTRITO", "DEPARTAMENTO", "MUNICIPIO", "ESTABLECIMIENTO",
    "DIRECCION", "TELEFONO", "SUPERVISOR", "DIRECTOR", "NIVEL", "SECTOR",
    "AREA", "STATUS", "MODALIDAD", "JORNADA", "PLAN", "DEPARTAMENTAL",
]
COLUMNAS_CATEGORICAS_SIMPLES = [
    "NIVEL", "SECTOR", "AREA", "STATUS", "MODALIDAD", "JORNADA", "PLAN", "DEPARTAMENTAL",
]

registro_transformaciones: list[dict] = []


def registrar(variable: str, problema: str, transformacion: str, registros_afectados: int, justificacion: str) -> None:
    registro_transformaciones.append(
        {
            "Variable": variable,
            "Problema detectado": problema,
            "Transformacion": transformacion,
            "Registros afectados": registros_afectados,
            "Justificacion": justificacion,
        }
    )


def cargar_crudo() -> pd.DataFrame:
    return pd.read_csv(ENTRADA, dtype=str, keep_default_na=False, encoding="utf-8")


def contar_faltantes_estilo_crudo(df: pd.DataFrame) -> tuple[int, int]:
    faltantes = 0
    variables_con_na = 0
    for col in COLUMNAS_ORIGINALES:
        n = int(df[col].map(es_placeholder_faltante).sum())
        faltantes += n
        variables_con_na += int(n > 0)
    return faltantes, variables_con_na


def snapshot_calidad_despues(df: pd.DataFrame) -> dict:
    columnas_dato = [c for c in COLUMNAS_ORIGINALES if c in df.columns]
    faltantes = int(df[columnas_dato].isna().sum().sum())
    variables_con_na = int((df[columnas_dato].isna().sum() > 0).sum())
    total_celdas = len(df) * len(columnas_dato)
    return {
        "Registros": len(df),
        "Variables": len(df.columns),
        "Valores faltantes": faltantes,
        "% faltantes": round(100 * faltantes / total_celdas, 2),
        "Variables con NA": variables_con_na,
        "Duplicados exactos": int(df[COLUMNAS_ORIGINALES].duplicated(keep=False).sum()),
    }


def limpiar(df_crudo: pd.DataFrame) -> pd.DataFrame:
    df = df_crudo.copy()

    # --- CODIGO ---------------------------------------------------------
    limpio, valido = Columnas.procesar_codigo(df["CODIGO"])
    df["CODIGO"] = limpio
    registrar(
        "CODIGO", "Ninguno: el 100% de los registros ya cumple ##-##-####-##.",
        "Se conserva como texto y se agrega verificacion de patron.",
        int((~valido).sum()),
        "Es un identificador, no una cantidad; convertirlo a numero perderia los guiones y ceros a la izquierda.",
    )

    # --- DISTRITO ---------------------------------------------------------
    limpio, clase, valido = Columnas.procesar_distrito(df["DISTRITO"])
    df["DISTRITO"] = limpio
    n_incompleto = int((clase == "incompleto").sum())
    n_vacio = int((clase == "vacio").sum())
    registrar(
        "DISTRITO",
        f"{n_vacio} vacios y {n_incompleto} truncados (ej. '01-' sin numero de distrito).",
        "Se documentan dos esquemas validos (##-### y ##-##-####) y se marca DISTRITO_VALIDO=False en vacios/truncados.",
        n_vacio + n_incompleto,
        "No se puede inventar el numero de distrito faltante; se deja explicito para seguimiento con la fuente.",
    )
    df["DISTRITO_FORMATO"] = clase
    df["DISTRITO_VALIDO"] = valido

    # --- DEPARTAMENTO -----------------------------------------------------
    limpio, valido = Columnas.procesar_departamento(df["DEPARTAMENTO"])
    n_tilde = int((limpio != df["DEPARTAMENTO"]).sum())
    df["DEPARTAMENTO"] = limpio
    registrar(
        "DEPARTAMENTO",
        "6 departamentos sin tilde (PETEN, QUICHE, SACATEPEQUEZ, SOLOLA, SUCHITEPEQUEZ, TOTONICAPAN).",
        "Se restaura la tilde oficial usando un catalogo de 22 departamentos + el caso especial CIUDAD CAPITAL.",
        n_tilde,
        "DEPARTAMENTAL (misma fuente) ya usa tilde para los mismos lugares; se unifica hacia la ortografia correcta, no hacia la mas frecuente.",
    )

    # --- MUNICIPIO ---------------------------------------------------------
    limpio, valido = Columnas.procesar_municipio(df["DEPARTAMENTO"], df["MUNICIPIO"])
    n_cambios = int((limpio != df["MUNICIPIO"]).sum())
    df["MUNICIPIO"] = limpio
    df["MUNICIPIO_VALIDO"] = valido
    registrar(
        "MUNICIPIO",
        f"Formato/tilde inconsistente en {n_cambios} registros; {int((~valido).sum())} fuera del catalogo oficial.",
        "Se normaliza contra el catalogo de municipios por departamento (fuente: Wikipedia/INE, verificado contra los datos). CIUDAD CAPITAL usa un dominio propio (ZONA 1..25).",
        n_cambios,
        "El catalogo se verifico contra los datos reales: los 'faltantes' son municipios pequenos sin ningun establecimiento de diversificado, no errores de escritura.",
    )

    # --- ESTABLECIMIENTO -----------------------------------------------------
    limpio, mapa_tildes = Columnas.procesar_establecimiento(df["ESTABLECIMIENTO"])
    n_cambios = int((limpio != df["ESTABLECIMIENTO"]).sum())
    df["ESTABLECIMIENTO"] = limpio
    registrar(
        "ESTABLECIMIENTO",
        "70 registros con comillas envolviendo el nombre completo; 446 grupos con variantes que solo difieren en tildes (incluye typos de acento grave).",
        "Se quitan comillas que envuelven TODO el campo (se conservan comillas internas, ej. COLEGIO \"LA PATRIA\"); se unifican variantes acento-insensibles hacia la forma con tilde correcta.",
        n_cambios,
        "No se cambia ninguna letra del nombre ni se corrigen typos reales: eso se deja para revision manual en el listado de duplicados parciales.",
    )

    # --- DIRECCION, SUPERVISOR, DIRECTOR (texto libre + placeholders) ------
    for col in ["DIRECCION", "SUPERVISOR", "DIRECTOR"]:
        limpio, mapa_tildes_col = Columnas.procesar_texto_libre_con_placeholder(df[col])
        registrar(
            col,
            "Vacios y placeholders ('-', '--', '.', 'S/D', 'SIN REGISTRO', etc.) mezclados como si fueran texto valido; "
            f"{len(mapa_tildes_col)} variantes que solo difieren en tildes (ej. nombres de personas escritos con y sin acento).",
            "Se normalizan espacios/caracteres invisibles/puntuacion suelta, se unifican variantes de tilde hacia la forma acentuada, y se convierten los placeholders a NA explicito.",
            int(limpio.isna().sum()),
            "Contar '---' como dato real subestima el porcentaje verdadero de valores faltantes; dos tildes distintas del mismo nombre no son dos personas distintas.",
        )
        df[col] = limpio

    # --- TELEFONO -----------------------------------------------------------
    resultado_tel = procesar_telefono(df["TELEFONO"].tolist())
    n_multiples = int((pd.Series(resultado_tel["TELEFONO_CANTIDAD"]) > 1).sum())
    n_invalidos = int((~pd.Series(resultado_tel["TELEFONO_VALIDO"])).sum())
    df["TELEFONO_ORIGINAL"] = df["TELEFONO"]
    df["TELEFONO"] = resultado_tel["TELEFONO"]
    df["TELEFONO_CANTIDAD"] = resultado_tel["TELEFONO_CANTIDAD"]
    df["TELEFONO_VALIDO"] = resultado_tel["TELEFONO_VALIDO"]
    df["TELEFONO_OBSERVACION"] = resultado_tel["TELEFONO_OBSERVACION"]
    registrar(
        "TELEFONO",
        "946 vacios; multiples numeros en una sola celda con separadores distintos (coma, '/', 'Y', guion); guion ambiguo (formato interno vs. separador vs. sufijo abreviado); presencia de FAX/extension/rangos.",
        "Se separan los numeros en una lista (TELEFONO), y se agregan TELEFONO_CANTIDAD, TELEFONO_VALIDO y TELEFONO_OBSERVACION. Los sufijos abreviados que comparten prefijo (ej. '22202870-73') se reconstruyen; TELEFONO_ORIGINAL conserva el valor crudo para auditoria.",
        n_multiples + n_invalidos,
        "Riesgo: la reconstruccion de sufijos asume que comparten el prefijo del numero anterior; queda expuesta en TELEFONO_ORIGINAL por si se debe revisar.",
    )

    # --- Categoricas de dominio pequeno (ya se verificaron limpias) --------
    for col in COLUMNAS_CATEGORICAS_SIMPLES:
        limpio = Columnas.procesar_categorica_simple(df[col])
        n_cambios = int((limpio != df[col]).sum())
        df[col] = limpio
        registrar(
            col,
            "Ninguno detectado en el perfilado (categorias ya uniformes en mayusculas).",
            "Se normalizan espacios/mayusculas de forma defensiva y se documenta el dominio observado.",
            n_cambios,
            "Se ejecuta igual sobre esta variable para dejar la verificacion explicita en el codigo, no solo asumida.",
        )

    return df


def verificar_consistencia_departamento_departamental(df: pd.DataFrame) -> str:
    """DEPARTAMENTAL reparte 'GUATEMALA' (departamento) en 4 zonas cardinales
    y 'QUICHE' en 2. Se comprueba que esa relacion se cumpla siempre (item
    5.h de la guia: consistencia entre variables)."""
    grupo_guatemala = {"GUATEMALA NORTE", "GUATEMALA OCCIDENTE", "GUATEMALA SUR", "GUATEMALA ORIENTE"}
    filas_guatemala = df[df["DEPARTAMENTO"].isin(["GUATEMALA", "CIUDAD CAPITAL"])]
    ok_guatemala = filas_guatemala["DEPARTAMENTAL"].isin(grupo_guatemala).all()
    otras_filas_con_zona_guatemala = df[~df["DEPARTAMENTO"].isin(["GUATEMALA", "CIUDAD CAPITAL"])]["DEPARTAMENTAL"].isin(grupo_guatemala).any()

    grupo_quiche = {"QUICHÉ", "QUICHÉ NORTE"}
    filas_quiche = df[df["DEPARTAMENTO"] == "QUICHÉ"]
    ok_quiche = filas_quiche["DEPARTAMENTAL"].isin(grupo_quiche).all()
    otras_filas_con_zona_quiche = df[df["DEPARTAMENTO"] != "QUICHÉ"]["DEPARTAMENTAL"].isin(grupo_quiche).any()

    consistente = ok_guatemala and not otras_filas_con_zona_guatemala and ok_quiche and not otras_filas_con_zona_quiche
    return (
        f"DEPARTAMENTO<->DEPARTAMENTAL consistente: {consistente} "
        f"(Guatemala/Ciudad Capital -> 4 zonas: {ok_guatemala}; Quiche -> 2 zonas: {ok_quiche})"
    )


def main() -> None:
    REPORTES_DIR.mkdir(parents=True, exist_ok=True)

    df_crudo = cargar_crudo()
    faltantes_antes, variables_con_na_antes = contar_faltantes_estilo_crudo(df_crudo)
    duplicados_exactos_antes = int(df_crudo.duplicated(keep=False).sum())
    unicos_establecimiento_antes = df_crudo["ESTABLECIMIENTO"].nunique()
    candidatos_antes = Duplicados.detectar_duplicados_parciales(df_crudo, umbral=90.0)
    parciales_antes = candidatos_antes[candidatos_antes["similitud_nombre"] < 100]

    df_limpio = limpiar(df_crudo)

    print(verificar_consistencia_departamento_departamental(df_limpio))
    n_municipio_invalido = int((~df_limpio["MUNICIPIO_VALIDO"]).sum())
    if n_municipio_invalido:
        print("Municipios fuera de catalogo tras la limpieza:")
        print(
            df_limpio.loc[~df_limpio["MUNICIPIO_VALIDO"], ["CODIGO", "DEPARTAMENTO", "MUNICIPIO"]]
            .drop_duplicates()
        )

    candidatos_despues = Duplicados.detectar_duplicados_parciales(df_limpio, umbral=90.0)
    # Los pares con 100% de similitud de nombre corresponden casi siempre al
    # mismo establecimiento con varios renglones (una fila por jornada/plan,
    # o por cambio de STATUS en el tiempo): se documentan aparte en vez de
    # mezclarlos con los candidatos reales de error ortografico/tipografico.
    parciales_despues = candidatos_despues[candidatos_despues["similitud_nombre"] < 100]
    nombres_repetidos = Duplicados.resumir_nombres_repetidos(df_limpio)
    nombres_repetidos_distinta_direccion = int((nombres_repetidos["direcciones_distintas"] > 1).sum())

    snapshot_antes = {
        "Registros": len(df_crudo),
        "Variables": len(df_crudo.columns),
        "Valores faltantes": faltantes_antes,
        "% faltantes": round(100 * faltantes_antes / (len(df_crudo) * len(COLUMNAS_ORIGINALES)), 2),
        "Variables con NA": variables_con_na_antes,
        "Duplicados exactos (fila completa)": duplicados_exactos_antes,
        "Posibles duplicados parciales (nombre similar, no identico)": len(parciales_antes),
        "Establecimientos unicos (ESTABLECIMIENTO)": unicos_establecimiento_antes,
    }
    snapshot_despues = snapshot_calidad_despues(df_limpio)
    snapshot_despues["Posibles duplicados parciales (nombre similar, no identico)"] = len(parciales_despues)
    snapshot_despues["Establecimientos unicos (ESTABLECIMIENTO)"] = df_limpio["ESTABLECIMIENTO"].nunique()
    snapshot_despues["Duplicados exactos (fila completa)"] = snapshot_despues.pop("Duplicados exactos")

    informe = pd.DataFrame(
        {
            "Metrica": list(snapshot_antes.keys()),
            "Antes": list(snapshot_antes.values()),
            "Despues": [snapshot_despues.get(k, "") for k in snapshot_antes.keys()],
        }
    )

    tabla_transformaciones = pd.DataFrame(registro_transformaciones)

    df_limpio.to_csv(SALIDA_CSV, index=False, encoding="utf-8")
    tabla_transformaciones.to_csv(REPORTES_DIR / "RegistroTransformaciones.csv", index=False, encoding="utf-8")
    informe.to_csv(REPORTES_DIR / "InformeCalidadAntesDespues.csv", index=False, encoding="utf-8")
    parciales_despues.to_csv(REPORTES_DIR / "PosiblesDuplicadosParciales.csv", index=False, encoding="utf-8")
    nombres_repetidos.to_csv(REPORTES_DIR / "EstablecimientosNombreRepetido.csv", index=False, encoding="utf-8")

    print()
    print("=== Informe de calidad: antes vs despues ===")
    print(informe.to_string(index=False))
    print()
    print(f"Dataset limpio: {SALIDA_CSV}")
    print(f"Registro de transformaciones: {REPORTES_DIR / 'RegistroTransformaciones.csv'} ({len(tabla_transformaciones)} filas)")
    print(f"Posibles duplicados parciales (nombre similar, no identico) para revision manual: {REPORTES_DIR / 'PosiblesDuplicadosParciales.csv'} ({len(parciales_despues)} pares)")
    print(
        f"Establecimientos con nombre repetido en el mismo municipio: {REPORTES_DIR / 'EstablecimientosNombreRepetido.csv'} "
        f"({len(nombres_repetidos)} grupos, {nombres_repetidos_distinta_direccion} con direccion distinta -> revisar esos primero)"
    )


if __name__ == "__main__":
    main()
