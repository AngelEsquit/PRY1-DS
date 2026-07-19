#!/usr/bin/env python3
"""
descargar_datos.py – Descarga automatizada de los .xls del portal MINEDUC.

Replica el proceso manual:
    seleccionar departamento → nivel DIVERSIFICADO → Consultar → guardar página.

Los archivos quedan en  Data/raw/{DEPARTAMENTO}.xls  como HTML con extensión
.xls, exactamente igual a lo que el navegador genera al hacer "Guardar como".

Uso desde terminal
------------------
    py descargar_datos.py                  # descarga solo los faltantes
    py descargar_datos.py --force          # re-descarga todos (backup previo)

Uso desde notebook / otro script
---------------------------------
    from descargar_datos import descargar
    resumen = descargar(raw_dir, force=True)
"""

from __future__ import annotations

import argparse
import random
import re
import shutil
import sys
import time
from pathlib import Path

try:
    import requests
except ImportError:
    sys.exit(
        "Error: el módulo 'requests' no está instalado.\n"
        "Ejecute:  py -m pip install requests"
    )

# ═══════════════════════════════════════════════════════════════════════════════
#  Configuración
# ═══════════════════════════════════════════════════════════════════════════════

BASE_URL = "https://www.mineduc.gob.gt/BUSCAESTABLECIMIENTO_GE/wbfBuscar.aspx"

# Mapa (código, nombre) extraído directamente del <select> del portal.
DEPARTAMENTOS: list[tuple[str, str]] = [
    ("16", "ALTA VERAPAZ"),
    ("15", "BAJA VERAPAZ"),
    ("04", "CHIMALTENANGO"),
    ("20", "CHIQUIMULA"),
    ("00", "CIUDAD CAPITAL"),
    ("02", "EL PROGRESO"),
    ("05", "ESCUINTLA"),
    ("01", "GUATEMALA"),
    ("13", "HUEHUETENANGO"),
    ("18", "IZABAL"),
    ("21", "JALAPA"),
    ("22", "JUTIAPA"),
    ("17", "PETEN"),
    ("09", "QUETZALTENANGO"),
    ("14", "QUICHE"),
    ("11", "RETALHULEU"),
    ("03", "SACATEPEQUEZ"),
    ("12", "SAN MARCOS"),
    ("06", "SANTA ROSA"),
    ("07", "SOLOLA"),
    ("10", "SUCHITEPEQUEZ"),
    ("08", "TOTONICAPAN"),
    ("19", "ZACAPA"),
]

NIVEL_DIVERSIFICADO = "46"

BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;"
        "q=0.9,image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "es-GT,es;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

DELAY_MIN = 2.0        # segundos entre departamentos
DELAY_MAX = 5.0
MAX_RETRIES = 3
TIMEOUT = 90            # segundos por petición HTTP


# ═══════════════════════════════════════════════════════════════════════════════
#  Utilidades
# ═══════════════════════════════════════════════════════════════════════════════

def resolve_project_root() -> Path:
    """Sube desde cwd (o desde el directorio del script) hasta encontrar Data/raw."""
    marker = Path("Data") / "raw"
    for candidate in [Path.cwd(), *Path.cwd().parents]:
        if (candidate / marker).exists():
            return candidate
    script_dir = Path(__file__).resolve().parent
    if (script_dir / marker).exists():
        return script_dir
    raise FileNotFoundError(
        f"No se encontró {marker} a partir de {Path.cwd()} ni en {script_dir}. "
        "Ejecute el script desde la raíz del repositorio."
    )


# Regex para extraer los campos ocultos de ASP.NET (__VIEWSTATE, etc.)
_HIDDEN_RE = re.compile(
    r'<input\s+type="hidden"\s+'
    r'name="(?P<name>[^"]+)"\s+'
    r'id="[^"]*"\s+'
    r'value="(?P<value>[^"]*)"',
    re.IGNORECASE,
)

# Regex para detectar códigos de establecimiento en la respuesta
_CODE_RE = re.compile(r"\d{2}-\d{2}-\d{4}-\d{2}")


def extract_hidden_fields(html: str) -> dict[str, str]:
    """Extrae __VIEWSTATE, __EVENTVALIDATION y demás campos ocultos."""
    return {m.group("name"): m.group("value") for m in _HIDDEN_RE.finditer(html)}


def extract_municipality_default(html: str) -> str:
    """Obtiene el valor por defecto del <select> de municipios tras el postback."""
    match = re.search(
        r'<select[^>]*name="_ctl0:ContentPlaceHolder1:cmbMunicipio"[^>]*>'
        r'\s*<option[^>]*value="([^"]*)"',
        html,
        re.IGNORECASE | re.DOTALL,
    )
    return match.group(1) if match else ""


def count_codes(html: str) -> int:
    """Cuenta cuántos códigos de establecimiento (##-##-####-##) hay en el HTML."""
    return len(_CODE_RE.findall(html))


# ═══════════════════════════════════════════════════════════════════════════════
#  Interacción con el formulario ASP.NET
# ═══════════════════════════════════════════════════════════════════════════════

def _build_form_data(
    hidden_fields: dict[str, str],
    dept_code: str,
    municipio: str = "",
    nivel: str = "TODOS",
    *,
    is_dept_postback: bool = False,
) -> dict[str, str]:
    """Construye el diccionario de datos POST para el formulario."""
    data: dict[str, str] = {}

    # Campos ocultos de ASP.NET
    for key in ("__VIEWSTATE", "__VIEWSTATEGENERATOR", "__EVENTVALIDATION"):
        if key in hidden_fields:
            data[key] = hidden_fields[key]

    if is_dept_postback:
        # Simula el AutoPostBack al cambiar el departamento
        data["__EVENTTARGET"] = "_ctl0$ContentPlaceHolder1$cmbDepartamento"
        data["__EVENTARGUMENT"] = ""
    else:
        data["__EVENTTARGET"] = ""
        data["__EVENTARGUMENT"] = ""

    # Campos del formulario
    data["_ctl0:ContentPlaceHolder1:cmbDepartamento"] = dept_code
    if municipio:
        data["_ctl0:ContentPlaceHolder1:cmbMunicipio"] = municipio
    data["_ctl0:ContentPlaceHolder1:cmbNivel"] = nivel
    data["_ctl0:ContentPlaceHolder1:cmbSector"] = "TODOS"
    data["_ctl0:ContentPlaceHolder1:ddlplan"] = "TODOS"
    data["_ctl0:ContentPlaceHolder1:ddlModalidad"] = "TODOS"
    data["_ctl0:ContentPlaceHolder1:txtCodEstab"] = ""
    data["_ctl0:ContentPlaceHolder1:txtNomEstab"] = ""
    data["_ctl0:ContentPlaceHolder1:txtDirecEstab"] = ""

    # Botón "Consultar" (image button → envía coordenadas .x .y)
    if not is_dept_postback:
        data["_ctl0:ContentPlaceHolder1:IbtnConsultar.x"] = str(
            random.randint(10, 80)
        )
        data["_ctl0:ContentPlaceHolder1:IbtnConsultar.y"] = str(
            random.randint(5, 25)
        )

    return data


def _get_page(session: requests.Session) -> requests.Response:
    """GET a la página principal (obtiene cookies y estado inicial)."""
    resp = session.get(BASE_URL, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp


def _post_form(
    session: requests.Session, data: dict[str, str]
) -> requests.Response:
    """POST al formulario."""
    resp = session.post(
        BASE_URL,
        data=data,
        timeout=TIMEOUT,
        headers={"Referer": BASE_URL},
    )
    resp.raise_for_status()
    return resp


# ═══════════════════════════════════════════════════════════════════════════════
#  Descarga de un departamento
# ═══════════════════════════════════════════════════════════════════════════════

def _download_one(
    session: requests.Session,
    hidden_fields: dict[str, str],
    dept_code: str,
    dept_name: str,
    output_path: Path,
) -> tuple[bool, dict[str, str], str]:
    """
    Descarga los datos de un departamento.

    Retorna (éxito, hidden_fields_actualizados, mensaje).
    """
    # ── Paso 1: postback de selección de departamento ──────────────────────
    dept_data = _build_form_data(
        hidden_fields, dept_code, is_dept_postback=True
    )
    try:
        dept_resp = _post_form(session, dept_data)
    except requests.RequestException as exc:
        return False, hidden_fields, f"error en postback de departamento: {exc}"

    dept_html = dept_resp.text
    dept_fields = extract_hidden_fields(dept_html)

    if not dept_fields.get("__VIEWSTATE"):
        return False, hidden_fields, "no se obtuvo __VIEWSTATE del postback"

    # Obtener el valor por defecto del municipio (normalmente "SELECCIONE UNO")
    muni_default = extract_municipality_default(dept_html)

    time.sleep(random.uniform(0.5, 1.5))

    # ── Paso 2: búsqueda con nivel DIVERSIFICADO ──────────────────────────
    search_data = _build_form_data(
        dept_fields,
        dept_code,
        municipio=muni_default,
        nivel=NIVEL_DIVERSIFICADO,
    )
    try:
        search_resp = _post_form(session, search_data)
    except requests.RequestException as exc:
        return False, dept_fields, f"error en búsqueda: {exc}"

    search_html = search_resp.text
    search_fields = extract_hidden_fields(search_html)

    # ── Paso 3: verificar que hay resultados ──────────────────────────────
    n_codes = count_codes(search_html)
    if n_codes == 0:
        # Fallback: intentar búsqueda directa (sin postback intermedio)
        search_data_direct = _build_form_data(
            hidden_fields,
            dept_code,
            nivel=NIVEL_DIVERSIFICADO,
        )
        try:
            search_resp = _post_form(session, search_data_direct)
        except requests.RequestException as exc:
            return False, hidden_fields, f"error en búsqueda directa: {exc}"

        search_html = search_resp.text
        search_fields = extract_hidden_fields(search_html)
        n_codes = count_codes(search_html)

        if n_codes == 0:
            return (
                False,
                search_fields or hidden_fields,
                "la respuesta no contiene datos de establecimientos",
            )

    # ── Paso 4: guardar como .xls ─────────────────────────────────────────
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Guardamos los bytes crudos tal cual llegaron del servidor, igual que
    # haría un navegador al hacer "Guardar como".  El encoding original
    # (latin-1 / ISO-8859-1) se preserva.
    with output_path.open("wb") as fh:
        fh.write(search_resp.content)

    size_kb = output_path.stat().st_size / 1024
    return (
        True,
        search_fields or hidden_fields,
        f"{n_codes} establecimientos, {size_kb:.0f} KB",
    )


# ═══════════════════════════════════════════════════════════════════════════════
#  Función pública
# ═══════════════════════════════════════════════════════════════════════════════

def descargar(
    raw_dir: Path,
    *,
    force: bool = False,
    backup_dir: Path | None = None,
    verbose: bool = True,
) -> dict[str, list[str]]:
    """
    Descarga los 23 archivos .xls del portal MINEDUC a *raw_dir*.

    Parámetros
    ----------
    raw_dir      Directorio de destino (normalmente ``Data/raw``).
    force        Si True, re-descarga incluso archivos que ya existen.
    backup_dir   Directorio donde copiar los .xls existentes antes de
                 sobreescribirlos (solo con ``force=True``).
    verbose      Imprimir progreso en consola.

    Retorna
    -------
    Diccionario con tres listas de nombres de departamento:
    ``{"descargados": [...], "omitidos": [...], "errores": [...]}``.
    """

    def _log(msg: str) -> None:
        if verbose:
            try:
                print(msg)
            except UnicodeEncodeError:
                safe_msg = (
                    msg.replace("⚠", "[!]")
                    .replace("✗", "[X]")
                    .replace("✓", "[OK]")
                    .replace("ó", "o")
                    .replace("Ó", "O")
                    .replace("á", "a")
                    .replace("é", "e")
                    .replace("í", "i")
                    .replace("ú", "u")
                    .replace("ñ", "n")
                )
                try:
                    print(safe_msg)
                except UnicodeEncodeError:
                    print(msg.encode("ascii", errors="replace").decode("ascii"))

    # -- Backup ------------------------------------------------------------
    if force and backup_dir is not None:
        existing = list(raw_dir.glob("*.xls"))
        if existing:
            backup_dir.mkdir(parents=True, exist_ok=True)
            backed = 0
            for f in existing:
                dest = backup_dir / f.name
                if not dest.exists():
                    shutil.copy2(f, dest)
                    backed += 1
            if backed:
                _log(f"Backup: {backed} archivos copiados a {backup_dir}")

    # -- Sesion HTTP -------------------------------------------------------
    session = requests.Session()
    session.headers.update(BROWSER_HEADERS)

    _log("Conectando al portal MINEDUC...")
    try:
        initial_resp = _get_page(session)
    except requests.RequestException as exc:
        raise ConnectionError(
            f"No se pudo conectar al portal MINEDUC: {exc}"
        ) from exc

    hidden_fields = extract_hidden_fields(initial_resp.text)
    if not hidden_fields.get("__VIEWSTATE"):
        raise RuntimeError(
            "No se pudo extraer __VIEWSTATE de la página inicial. "
            "Es posible que el sitio esté bloqueando la petición."
        )

    _log(
        f"Conexion establecida. Descargando {len(DEPARTAMENTOS)} departamentos...\n"
    )

    # -- Descarga ----------------------------------------------------------
    descargados: list[str] = []
    omitidos: list[str] = []
    errores: list[str] = []

    total = len(DEPARTAMENTOS)
    for i, (code, name) in enumerate(DEPARTAMENTOS, 1):
        output_path = raw_dir / f"{name}.xls"

        # Modo incremental
        if output_path.exists() and not force:
            _log(f"  [{i:2d}/{total}] {name}: omitido (ya existe)")
            omitidos.append(name)
            continue

        _log(f"  [{i:2d}/{total}] {name}: descargando...")

        success = False
        for attempt in range(1, MAX_RETRIES + 1):
            ok, hidden_fields, msg = _download_one(
                session, hidden_fields, code, name, output_path
            )
            if ok:
                _log(f"           -> {msg}")
                descargados.append(name)
                success = True
                break

            _log(f"           [!] intento {attempt}/{MAX_RETRIES}: {msg}")

            if attempt < MAX_RETRIES:
                wait = 2**attempt + random.uniform(0, 2)
                _log(f"           esperando {wait:.0f}s antes de reintentar...")
                time.sleep(wait)
                # Refrescar sesión desde cero
                try:
                    fresh = _get_page(session)
                    hidden_fields = extract_hidden_fields(fresh.text)
                except Exception:
                    pass  # se reintenta con los campos anteriores

        if not success:
            _log(f"           [X] FALLO despues de {MAX_RETRIES} intentos")
            errores.append(name)

        # Pausa entre departamentos
        if i < total:
            time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))

    # -- Resumen -----------------------------------------------------------
    _log("\n" + "=" * 60)
    _log("RESUMEN DE DESCARGA")
    _log("=" * 60)
    _log(
        f"  Descargados : {len(descargados)}\n"
        f"  Omitidos    : {len(omitidos)}\n"
        f"  Errores     : {len(errores)}"
    )
    if errores:
        _log(f"\n[!] Departamentos con error: {', '.join(errores)}")
        _log("  Puede reintentar ejecutando el script de nuevo.")
    else:
        _log(f"\n[OK] Todos los archivos estan en {raw_dir}")

    return {
        "descargados": descargados,
        "omitidos": omitidos,
        "errores": errores,
    }


# ═══════════════════════════════════════════════════════════════════════════════
#  CLI
# ═══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Descarga archivos .xls del portal MINEDUC "
            "(establecimientos de nivel Diversificado)."
        )
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-descarga todos los archivos, incluso los que ya existen.",
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="No crear backup de archivos existentes al usar --force.",
    )
    args = parser.parse_args()

    root = resolve_project_root()
    raw_dir = root / "Data" / "raw"
    backup_dir = None if args.no_backup else (root / "Data" / "raw_backup")

    result = descargar(raw_dir, force=args.force, backup_dir=backup_dir)

    if result["errores"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
