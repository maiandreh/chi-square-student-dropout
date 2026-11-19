"""Obtém um snapshot do dataset UCI 697 sem exigir resultados estatísticos fixos.

A aquisição deve registrar os dados efetivamente retornados pela fonte, mesmo
quando eles diferem da tabela de referência. Execute validar_base_uci.py para
conferir a compatibilidade antes de comparar os resultados estatísticos.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import pyarrow
from ucimlrepo import fetch_ucirepo

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
SOURCE = "https://archive.ics.uci.edu/dataset/697/predict+students+dropout+and+academic+success"
DOI = "10.24432/C5MC89"
DATASET_ID = 697


def salvar_snapshot(df: pd.DataFrame, pasta: Path = RAW) -> tuple[Path, Path]:
    """Salva snapshot e manifesto; não sobrescreve aquisições anteriores."""
    if not isinstance(df, pd.DataFrame) or df.empty:
        raise ValueError("A fonte não retornou um DataFrame não vazio")

    obtido_em = datetime.now(timezone.utc)
    carimbo = obtido_em.strftime("%Y%m%dT%H%M%S%fZ")
    pasta.mkdir(parents=True, exist_ok=True)
    prefixo = pasta / f"uci697_obtido_{carimbo}"
    parquet = prefixo.with_suffix(".parquet")
    manifesto = pasta / f"{prefixo.name}_metadata.json"
    if parquet.exists() or manifesto.exists():
        raise FileExistsError("Snapshot com este carimbo já existe")

    # A cópia Parquet não é uma réplica binária dos arquivos originais da UCI.
    df.to_parquet(parquet, index=False, engine="pyarrow")
    digest = hashlib.sha256(parquet.read_bytes()).hexdigest()
    metadados = {
        "dataset_id": DATASET_ID,
        "doi": DOI,
        "source_url": SOURCE,
        "retrieved_at_utc": obtido_em.isoformat(timespec="microseconds"),
        "snapshot_file": parquet.name,
        "sha256_parquet": digest,
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "column_names": list(df.columns),
        "pandas_version": pd.__version__,
        "pyarrow_version": pyarrow.__version__,
        "retrieval_client": "ucimlrepo.fetch_ucirepo(id=697)",
        "validation": "Pendente: executar src/validar_base_uci.py",
    }
    try:
        manifesto.write_text(
            json.dumps(metadados, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    except OSError:
        parquet.unlink(missing_ok=True)
        raise
    return parquet, manifesto


def main() -> None:
    conjunto = fetch_ucirepo(id=DATASET_ID)
    parquet, manifesto = salvar_snapshot(conjunto.data.original)
    print(f"Snapshot: {parquet}")
    print(f"Proveniência: {manifesto}")
    print(f"Valide com: python src/validar_base_uci.py {parquet}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Erro ao obter base UCI: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
