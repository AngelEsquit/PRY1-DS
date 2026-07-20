"""
tests/test_calidad_dataset_limpio.py

Pruebas automáticas que verifican la calidad del conjunto de datos limpio
(EstablecimientosDiversificadoLimpio.csv) conforme a la actividad 7 de la
guía del Proyecto 1 – Data Science 2026.

Ejecutar con:
    pytest tests/ -v

Requisito previo: haber ejecutado notebooks/02_limpieza_y_validacion.ipynb
para que exista Data/csv/EstablecimientosDiversificadoLimpio.csv.
"""

import re
from pathlib import Path

import pandas as pd
import pytest

# ---------------------------------------------------------------------------
# Fixture: carga el dataset limpio una sola vez para todos los tests
# ---------------------------------------------------------------------------

def _find_root() -> Path:
    """Sube desde el directorio de tests hasta encontrar la raíz del proyecto."""
    candidate = Path(__file__).resolve().parent.parent
    if (candidate / "Data").exists():
        return candidate
    raise FileNotFoundError(
        "No se encontró el directorio 'Data/' a partir de la ubicación del test. "
        "Ejecute pytest desde la raíz del repositorio."
    )


@pytest.fixture(scope="session")
def df() -> pd.DataFrame:
    """Carga Data/csv/EstablecimientosDiversificadoLimpio.csv."""
    root = _find_root()
    csv_path = root / "Data" / "csv" / "EstablecimientosDiversificadoLimpio.csv"
    assert csv_path.exists(), (
        f"No se encontró el dataset limpio en {csv_path}. "
        "Ejecute primero notebooks/02_limpieza_y_validacion.ipynb."
    )
    return pd.read_csv(csv_path, dtype=str, keep_default_na=False, na_values=[""])


# ---------------------------------------------------------------------------
# Catálogos de validación
# ---------------------------------------------------------------------------

DEPARTAMENTOS_VALIDOS = {
    "ALTA VERAPAZ", "BAJA VERAPAZ", "CHIMALTENANGO", "CHIQUIMULA",
    "CIUDAD CAPITAL", "EL PROGRESO", "ESCUINTLA", "GUATEMALA",
    "HUEHUETENANGO", "IZABAL", "JALAPA", "JUTIAPA", "PETÉN",
    "QUETZALTENANGO", "QUICHÉ", "RETALHULEU", "SACATEPÉQUEZ",
    "SAN MARCOS", "SANTA ROSA", "SOLOLÁ", "SUCHITEPÉQUEZ",
    "TOTONICAPÁN", "ZACAPA",
}

NIVELES_VALIDOS = {"DIVERSIFICADO"}
# 'SIN ESPECIFICAR' aparece en el dataset crudo y se documenta en el diagnóstico
# como un valor de dominio propio del MINEDUC (no es un error de escritura).
AREAS_VALIDAS = {"URBANA", "RURAL", "SIN ESPECIFICAR"}
SECTORES_VALIDOS = {"OFICIAL", "PRIVADO", "MUNICIPAL", "COOPERATIVA"}
# El MINEDUC usa variantes adicionales de STATUS que no se eliminaron porque
# son categorías reales de la fuente primaria.
STATUS_VALIDOS = {
    "ABIERTA",
    "CERRADA DEFINITIVAMENTE",
    "CERRADA TEMPORALMENTE",
    "TEMPORAL TITULOS",
    "TEMPORAL NOMBRAMIENTO",
}
MODALIDADES_VALIDAS = {"MONOLINGUE", "BILINGUE"}

PATRON_CODIGO = re.compile(r"^\d{2}-\d{2}-\d{4}-\d{2}$")
PATRON_TELEFONO_SIMPLE = re.compile(r"^\d{7,8}$")   # un solo número limpio


# ---------------------------------------------------------------------------
# 1. Estructura básica
# ---------------------------------------------------------------------------

class TestEstructura:
    def test_dataset_no_vacio(self, df):
        """El dataset debe tener al menos un registro."""
        assert len(df) > 0, "El dataset está vacío."

    def test_columnas_minimas_presentes(self, df):
        """Las 17 columnas originales deben existir en el limpio."""
        columnas_requeridas = {
            "CODIGO", "DISTRITO", "DEPARTAMENTO", "MUNICIPIO",
            "ESTABLECIMIENTO", "DIRECCION", "TELEFONO", "SUPERVISOR",
            "DIRECTOR", "NIVEL", "SECTOR", "AREA", "STATUS",
            "MODALIDAD", "JORNADA", "PLAN", "DEPARTAMENTAL",
        }
        faltantes = columnas_requeridas - set(df.columns)
        assert not faltantes, f"Columnas faltantes en el limpio: {sorted(faltantes)}"


# ---------------------------------------------------------------------------
# 2. Sin duplicados exactos (ítem 7 de la guía)
# ---------------------------------------------------------------------------

class TestDuplicados:
    def test_sin_duplicados_exactos(self, df):
        """No debe haber filas completamente idénticas."""
        duplicados = df.duplicated(keep=False).sum()
        assert duplicados == 0, (
            f"Se encontraron {duplicados} filas que forman duplicados exactos."
        )


# ---------------------------------------------------------------------------
# 3. Sin espacios al inicio/final en columnas de texto (ítem 7 de la guía)
# ---------------------------------------------------------------------------

class TestEspacios:
    COLUMNAS_TEXTO = [
        "CODIGO", "DISTRITO", "DEPARTAMENTO", "MUNICIPIO",
        "ESTABLECIMIENTO", "DIRECCION", "SUPERVISOR", "DIRECTOR",
        "NIVEL", "SECTOR", "AREA", "STATUS", "MODALIDAD", "JORNADA",
        "PLAN", "DEPARTAMENTAL",
    ]

    def test_sin_espacios_borde(self, df):
        """Ningún valor en columnas de texto debe empezar o terminar con espacio."""
        errores = []
        for col in self.COLUMNAS_TEXTO:
            if col not in df.columns:
                continue
            serie = df[col].dropna()
            con_espacio = serie[serie != serie.str.strip()]
            if not con_espacio.empty:
                errores.append(
                    f"  {col}: {len(con_espacio)} valor(es) con espacio al borde "
                    f"(ej. {repr(con_espacio.iloc[0])})"
                )
        assert not errores, (
            "Columnas con espacios al inicio/final tras la limpieza:\n"
            + "\n".join(errores)
        )


# ---------------------------------------------------------------------------
# 4. Dominio de variables categóricas cerradas (ítem 7 de la guía)
# ---------------------------------------------------------------------------

class TestDominios:
    def test_nivel_solo_diversificado(self, df):
        """NIVEL sólo debe contener 'DIVERSIFICADO' (era el filtro original)."""
        fuera = set(df["NIVEL"].dropna().unique()) - NIVELES_VALIDOS
        assert not fuera, f"Valores inesperados en NIVEL: {fuera}"

    def test_area_valida(self, df):
        fuera = set(df["AREA"].dropna().unique()) - AREAS_VALIDAS
        assert not fuera, f"Valores inesperados en AREA: {fuera}"

    def test_sector_valido(self, df):
        fuera = set(df["SECTOR"].dropna().unique()) - SECTORES_VALIDOS
        assert not fuera, f"Valores inesperados en SECTOR: {fuera}"

    def test_status_valido(self, df):
        fuera = set(df["STATUS"].dropna().unique()) - STATUS_VALIDOS
        assert not fuera, f"Valores inesperados en STATUS: {fuera}"

    def test_modalidad_valida(self, df):
        fuera = set(df["MODALIDAD"].dropna().unique()) - MODALIDADES_VALIDAS
        assert not fuera, f"Valores inesperados en MODALIDAD: {fuera}"


# ---------------------------------------------------------------------------
# 5. Validez del campo CODIGO (ítem 7 de la guía)
# ---------------------------------------------------------------------------

class TestCodigo:
    def test_codigo_patron(self, df):
        """Todos los CODIGO deben cumplir el patrón ##-##-####-##."""
        invalidos = df["CODIGO"].dropna()[
            ~df["CODIGO"].dropna().str.match(PATRON_CODIGO)
        ]
        assert invalidos.empty, (
            f"CODIGO con formato inválido ({len(invalidos)} casos): "
            f"{invalidos.head(5).tolist()}"
        )

    def test_codigo_sin_nulos(self, df):
        """CODIGO no debe tener valores faltantes (es el identificador único)."""
        nulos = df["CODIGO"].isna().sum()
        assert nulos == 0, f"CODIGO tiene {nulos} valor(es) nulo(s)."


# ---------------------------------------------------------------------------
# 6. Departamentos pertenecen al catálogo oficial (ítem 7 de la guía)
# ---------------------------------------------------------------------------

class TestDepartamentos:
    def test_departamentos_en_catalogo(self, df):
        """Los valores de DEPARTAMENTO deben estar en el catálogo oficial."""
        observados = set(df["DEPARTAMENTO"].dropna().unique())
        fuera = observados - DEPARTAMENTOS_VALIDOS
        assert not fuera, (
            f"Departamentos no reconocidos en el catálogo: {sorted(fuera)}"
        )


# ---------------------------------------------------------------------------
# 7. Teléfonos con formato consistente (ítem 7 de la guía)
# ---------------------------------------------------------------------------

class TestTelefono:
    def test_telefono_solo_digitos_o_multiples_limpios(self, df):
        """Cada número individual en TELEFONO debe ser sólo dígitos de 7 u 8 cifras.
        TELEFONO puede contener varios números separados por '; ', todos deben ser válidos.
        """
        if "TELEFONO" not in df.columns:
            pytest.skip("Columna TELEFONO no presente.")

        errores = []
        for valor in df["TELEFONO"].dropna():
            partes = [p.strip() for p in str(valor).split(";") if p.strip()]
            for parte in partes:
                if not PATRON_TELEFONO_SIMPLE.match(parte):
                    errores.append(repr(parte))
                    if len(errores) >= 10:
                        break
            if len(errores) >= 10:
                break

        assert not errores, (
            f"Teléfonos con formato inválido (primeros {len(errores)}):\n"
            + "\n".join(f"  {e}" for e in errores)
        )

    def test_telefono_valido_es_booleano_y_coherente(self, df):
        """TELEFONO_VALIDO debe ser una bandera booleana coherente:
        sólo True/False, y ninguna fila sin teléfono puede quedar marcada
        como válida.
        """
        if "TELEFONO_VALIDO" not in df.columns:
            pytest.skip("Columna TELEFONO_VALIDO no presente (notebook 02 no ejecutado).")

        valores = set(df["TELEFONO_VALIDO"].dropna().astype(str).unique())
        assert valores <= {"True", "False"}, (
            f"TELEFONO_VALIDO tiene valores no booleanos: {valores}"
        )

        sin_telefono_pero_valido = df[
            df["TELEFONO"].isna() & (df["TELEFONO_VALIDO"].astype(str) == "True")
        ]
        assert sin_telefono_pero_valido.empty, (
            f"{len(sin_telefono_pero_valido)} fila(s) sin teléfono marcadas como "
            "TELEFONO_VALIDO=True."
        )


# ---------------------------------------------------------------------------
# 8. Sin categorías duplicadas por diferencias de escritura (ítem 7 de la guía)
# ---------------------------------------------------------------------------

class TestCategoriasConsistentes:
    COLUMNAS_CATEGORICAS = [
        "DEPARTAMENTO", "NIVEL", "SECTOR", "AREA",
        "STATUS", "MODALIDAD", "JORNADA", "PLAN",
    ]

    def test_sin_mezcla_mayusculas_minusculas(self, df):
        """Ninguna columna categórica debe tener el mismo valor en mayúsculas y minúsculas."""
        errores = []
        for col in self.COLUMNAS_CATEGORICAS:
            if col not in df.columns:
                continue
            valores = df[col].dropna().unique()
            normalizados = [v.upper() for v in valores]
            vistos = {}
            for orig, norm in zip(valores, normalizados):
                if norm in vistos and vistos[norm] != orig:
                    errores.append(
                        f"  {col}: '{orig}' vs '{vistos[norm]}' "
                        "(misma cadena, distinto case)"
                    )
                else:
                    vistos[norm] = orig
        assert not errores, (
            "Categorías duplicadas por diferencias de escritura:\n"
            + "\n".join(errores)
        )


# ---------------------------------------------------------------------------
# 9. Tipos de datos esperados (ítem 7 de la guía)
# ---------------------------------------------------------------------------

class TestTipos:
    def test_codigo_es_string(self, df):
        """CODIGO debe ser texto (no número), porque tiene guiones.

        pandas ≥ 2.0 puede devolver StringDtype en lugar de object cuando
        se lee con dtype=str; ambos representan texto y son aceptables.
        """
        dtype_name = str(df["CODIGO"].dtype)
        assert "str" in dtype_name or df["CODIGO"].dtype == object, (
            f"CODIGO tiene dtype {df['CODIGO'].dtype}, "
            "se esperaba un tipo de texto (object o StringDtype)."
        )

    def test_telefono_cantidad_es_numerico(self, df):
        """TELEFONO_CANTIDAD, si existe, debe ser convertible a int."""
        if "TELEFONO_CANTIDAD" not in df.columns:
            pytest.skip("TELEFONO_CANTIDAD no está en el dataset.")
        try:
            df["TELEFONO_CANTIDAD"].dropna().astype(int)
        except (ValueError, TypeError) as exc:
            pytest.fail(f"TELEFONO_CANTIDAD no es numérico: {exc}")
