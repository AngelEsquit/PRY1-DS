from __future__ import annotations

import csv
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DATOS_DIR = ROOT / "Datos" / "Raw"
CSV_DIR = ROOT / "Datos" / "Csv"
TMP_DIR = ROOT / "Datos" / ".tmp_csv_export"
CONSOLIDATED_NAME = "EstablecimientosDiversificadoConsolidado.csv"

EXPECTED_HEADERS = [
    "CODIGO",
    "DISTRITO",
    "DEPARTAMENTO",
    "MUNICIPIO",
    "ESTABLECIMIENTO",
    "DIRECCION",
    "TELEFONO",
    "SUPERVISOR",
    "DIRECTOR",
    "NIVEL",
    "SECTOR",
    "AREA",
    "STATUS",
    "MODALIDAD",
    "JORNADA",
    "PLAN",
    "DEPARTAMENTAL",
]

CODE_PATTERN = re.compile(r"^\d{2}-\d{2}-\d{4}-\d{2}$")


def normalize_cell(value: str) -> str:
    return value.strip()


def find_header_index(rows: list[list[str]]) -> int:
    for index, row in enumerate(rows):
        if not row:
            continue
        first = row[0].strip().upper()
        if first == "CODIGO" and any(cell.strip().upper() == "ESTABLECIMIENTO" for cell in row):
            return index
    raise ValueError("No se encontro la fila de encabezados esperada")


def export_xls_to_csv(xls_path: Path, destination_dir: Path) -> Path:
    destination_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "libreoffice",
            "--headless",
            "--convert-to",
            "csv",
            "--outdir",
            str(destination_dir),
            str(xls_path),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    csv_path = destination_dir / f"{xls_path.stem}.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"No se genero el CSV esperado para {xls_path.name}")
    return csv_path


def read_rows(csv_path: Path) -> list[list[str]]:
    with csv_path.open(newline="", encoding="utf-8", errors="replace") as handle:
        return list(csv.reader(handle))


def extract_table(rows: list[list[str]]) -> list[list[str]]:
    header_index = find_header_index(rows)
    cleaned_rows: list[list[str]] = []
    for row in rows[header_index + 1 :]:
        if not row:
            continue
        if not CODE_PATTERN.match(row[0].strip()):
            continue
        normalized = [normalize_cell(cell) for cell in row[: len(EXPECTED_HEADERS)]]
        if len(normalized) < len(EXPECTED_HEADERS):
            normalized.extend([""] * (len(EXPECTED_HEADERS) - len(normalized)))
        cleaned_rows.append(normalized)
    return cleaned_rows


def write_csv(csv_path: Path, rows: list[list[str]]) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(EXPECTED_HEADERS)
        writer.writerows(rows)


def main() -> None:
    csv_dir = CSV_DIR
    tmp_dir = TMP_DIR
    csv_dir.mkdir(parents=True, exist_ok=True)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    consolidated_rows: list[list[str]] = []
    summary: list[tuple[str, int]] = []

    xls_files = sorted(DATOS_DIR.glob("*.xls"))
    if not xls_files:
        raise FileNotFoundError("No se encontraron archivos .xls dentro de Datos/")

    for xls_file in xls_files:
        temp_csv = export_xls_to_csv(xls_file, tmp_dir)
        rows = read_rows(temp_csv)
        table_rows = extract_table(rows)
        write_csv(csv_dir / f"{xls_file.stem}.csv", table_rows)
        consolidated_rows.extend(table_rows)
        summary.append((xls_file.name, len(table_rows)))

    write_csv(csv_dir / CONSOLIDATED_NAME, consolidated_rows)

    print("Archivos procesados:")
    total_rows = 0
    for name, count in summary:
        print(f"- {name}: {count} filas")
        total_rows += count
    print(f"Total consolidado: {total_rows} filas")
    print(f"Salida principal: {csv_dir / CONSOLIDATED_NAME}")


if __name__ == "__main__":
    main()