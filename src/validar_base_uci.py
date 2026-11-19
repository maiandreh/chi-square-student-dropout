"""Valida um snapshot UCI 697 contra as frequências de referência versionadas.

Uso: python src/validar_base_uci.py data/raw/uci697_obtido_....parquet
O arquivo de aquisição é preservado mesmo quando a comparação falha.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
TABLE = ROOT / "data" / "processed" / "frequencias_observadas_bolsa_situacao.csv"
RESULTS = ROOT / "results"
LABELS = ("Dropout", "Enrolled", "Graduate")
SCHOLARSHIP = {"sem_bolsa": "0", "com_bolsa": "1"}


def referencia(arquivo: Path = TABLE) -> dict[tuple[str, str], int]:
    """Obtém as seis contagens diretamente da tabela CSV versionada."""
    with arquivo.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if set(row["bolsa"] for row in rows) != set(SCHOLARSHIP) or len(rows) != 2:
        raise ValueError("Grupos de bolsas inesperados na referência")
    return {
        (SCHOLARSHIP[row["bolsa"]], label): int(row[label.lower()])
        for row in rows
        for label in LABELS
    }


def frequencias(df: pd.DataFrame) -> dict[tuple[str, str], int]:
    """Conta os pares bolsa/desfecho, sem descartar categorias inesperadas."""
    required = {"Scholarship holder", "Target"}
    if not required.issubset(df.columns):
        raise ValueError(f"Colunas obrigatórias ausentes: {required - set(df.columns)}")
    bolsa = pd.to_numeric(df["Scholarship holder"], errors="raise")
    desfecho = df["Target"].astype("string").str.strip()
    if bolsa.isna().any() or desfecho.isna().any():
        raise ValueError("Há valores ausentes nas variáveis de análise")
    if (bolsa % 1 != 0).any():
        raise ValueError("Valores não inteiros em Scholarship holder")
    return dict(Counter(zip(bolsa.astype(int).astype(str), desfecho)))


def validar(df: pd.DataFrame, esperado: dict | None = None) -> dict:
    """Compara contagens e dimensões; não altera a base recuperada."""
    esperado = referencia() if esperado is None else esperado
    obtido = frequencias(df)
    chaves = sorted(set(obtido) | set(esperado))
    divergencias = [
        {"bolsa": key[0], "situacao": key[1],
         "esperado": esperado.get(key, 0), "observado": obtido.get(key, 0)}
        for key in chaves if obtido.get(key, 0) != esperado.get(key, 0)
    ]
    status = "compativel" if not divergencias and len(df) == sum(esperado.values()) else "divergente"
    return {
        "status": status,
        "rows": int(len(df)),
        "rows_reference": sum(esperado.values()),
        "columns": int(len(df.columns)),
        "divergencias": divergencias,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot", type=Path, help="Snapshot .parquet obtido da UCI")
    args = parser.parse_args()
    if args.snapshot.suffix.lower() != ".parquet":
        parser.error("Informe um arquivo .parquet")

    df = pd.read_parquet(args.snapshot)
    relatorio = validar(df)
    relatorio["snapshot"] = args.snapshot.name
    relatorio["validado_em_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    relatorio["sha256_parquet"] = hashlib.sha256(args.snapshot.read_bytes()).hexdigest()
    RESULTS.mkdir(exist_ok=True)
    destino = RESULTS / f"{args.snapshot.stem}_validacao.json"
    destino.write_text(json.dumps(relatorio, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Validação: {relatorio['status']}")
    print(f"Relatório: {destino}")
    if relatorio["divergencias"]:
        for item in relatorio["divergencias"]:
            print(f"  {item['bolsa']}/{item['situacao']}: "
                  f"esperado={item['esperado']}, observado={item['observado']}")
    return 0 if relatorio["status"] == "compativel" else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError) as exc:
        print(f"Erro na validação: {exc}", file=sys.stderr)
        sys.exit(2)
