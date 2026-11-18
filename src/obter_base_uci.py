"""Obtém a UCI 697 diretamente pelo cliente oficial e preserva um snapshot.

Requer rede, ucimlrepo, pandas e pyarrow. Nenhum dado original é enviado ao Git.
O timestamp corresponde à conclusão da obtenção (UTC), não à data de publicação.
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

# Tabela publicada na Entrega 3, usada exclusivamente para verificação.
EXPECTED = {
    ("0", "Dropout"): 1287, ("0", "Enrolled"): 664, ("0", "Graduate"): 1374,
    ("1", "Dropout"): 134, ("1", "Enrolled"): 130, ("1", "Graduate"): 835,
}


def count_outcomes(df: pd.DataFrame) -> dict[tuple[str, str], int]:
    """Retorna todas as combinações observadas, inclusive eventuais inesperadas."""
    required = {"Scholarship holder", "Target"}
    if not required.issubset(df.columns):
        raise ValueError(f"Colunas obrigatórias ausentes: {sorted(required - set(df.columns))}")
    scholarships = pd.to_numeric(df["Scholarship holder"], errors="raise")
    if scholarships.isna().any() or not scholarships.isin([0, 1]).all():
        raise ValueError("Scholarship holder contém valores inesperados")
    targets = df["Target"].astype("string").str.strip()
    if targets.isna().any():
        raise ValueError("Target contém valores ausentes")
    pairs = zip(scholarships.astype(int).astype(str), targets)
    from collections import Counter
    return dict(Counter(pairs))


def main() -> None:
    """Consulta a UCI, carimba o snapshot e registra proveniência e hash SHA-256."""
    dataset = fetch_ucirepo(id=DATASET_ID)
    df = dataset.data.original
    if not isinstance(df, pd.DataFrame):
        raise TypeError("A UCI não retornou um DataFrame para data.original")
    if len(df) != 4424 or len(df.columns) != 37:
        raise ValueError(f"Estrutura inesperada: {len(df)} linhas × {len(df.columns)} colunas")

    counts = count_outcomes(df)
    if counts != EXPECTED:
        raise ValueError(
            "As contagens diferem da Entrega 3; nenhum snapshot será salvo. "
            f"Contagens obtidas: {counts}"
        )

    # Momento de aquisição registrado somente após retorno e conferência.
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    RAW.mkdir(parents=True, exist_ok=True)
    base = RAW / f"uci697_obtido_{stamp}"
    parquet = base.with_suffix(".parquet")
    metadata = base.with_name(base.name + "_metadata.json")

    # Não sobrescrever uma aquisição anterior, mesmo com timestamp coincidente.
    if parquet.exists() or metadata.exists():
        raise FileExistsError(f"Snapshot já existente: {base.name}")

    df.to_parquet(parquet, index=False, engine="pyarrow")
    digest = hashlib.sha256(parquet.read_bytes()).hexdigest()
    manifest = {
        "dataset_id": DATASET_ID,
        "doi": DOI,
        "source_url": SOURCE,
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "snapshot_file": parquet.name,
        "sha256_parquet": digest,
        "rows": len(df), "columns": len(df.columns),
        "pandas_version": pd.__version__, "pyarrow_version": pyarrow.__version__,
        "retrieval_client": "ucimlrepo.fetch_ucirepo(id=697)",
        "matches_entrega3_counts": True,
        "historical_source_equivalence": (
            "Contagens coincidentes não provam identidade byte a byte com a cópia de 2026."
        ),
    }
    metadata.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Snapshot salvo: {parquet}")
    print(f"Metadados: {metadata}")
    print(f"SHA-256: {digest}")
    print("Conferência das seis contagens: OK")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Falha na obtenção: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
