"""Reproduz o teste de Pearson a partir da tabela publicada na Entrega 3.

Este cálculo não constitui nova extração nem autenticação do CSV oficial.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np
from scipy.stats import chi2_contingency

BASE = Path(__file__).resolve().parent.parent
COLUNAS = ("dropout", "enrolled", "graduate")
GRUPOS = ("sem_bolsa", "com_bolsa")


def carregar_observados(base_parquet: Path | None = None) -> np.ndarray:
    """Lê a tabela histórica ou monta contagens diretamente de um snapshot Parquet."""
    if base_parquet is not None:
        import pandas as pd
        df = pd.read_parquet(base_parquet)
        if not {"Scholarship holder", "Target"}.issubset(df.columns):
            raise ValueError("O snapshot não contém Scholarship holder e Target")
        bolsa = pd.to_numeric(df["Scholarship holder"], errors="raise")
        target = df["Target"].astype("string").str.strip()
        if bolsa.isna().any() or not bolsa.isin([0, 1]).all() or target.isna().any():
            raise ValueError("Valores inesperados de bolsa ou desfecho")
        tabela = pd.crosstab(bolsa.astype(int), target)
        expected_cols = ["Dropout", "Enrolled", "Graduate"]
        if set(tabela.columns) != set(expected_cols) or set(tabela.index) != {0, 1}:
            raise ValueError("Categorias incompatíveis com a tabela da Entrega 3")
        observados = tabela.loc[[0, 1], expected_cols].to_numpy(dtype=int)
        if observados.shape != (2, 3) or observados.sum() != 4424:
            raise ValueError("Total ou formato inesperado no snapshot UCI")
        return observados
    with (BASE / "data" / "processed" / "tabela_observada_entrega3.csv").open(encoding="utf-8", newline="") as arquivo:
        linhas = list(csv.DictReader(arquivo))
    if [linha["bolsa"] for linha in linhas] != list(GRUPOS):
        raise ValueError("Grupos diferentes dos registrados na Entrega 3")
    observados = np.array([[int(linha[c]) for c in COLUNAS] for linha in linhas], dtype=int)
    if observados.shape != (2, 3) or (observados < 0).any() or observados.sum() != 4424:
        raise ValueError("Tabela inconsistente com a Entrega 3")
    return observados


def calcular(base_parquet: Path | None = None) -> dict:
    """Calcula esperados, contribuições, estatística, p-valor e V de Cramér."""
    o = carregar_observados(base_parquet)
    # A correção de Yates não se aplica à presente tabela 2 × 3.
    qui2, p, gl, esperadas = chi2_contingency(o, correction=False)
    # V = raiz[qui2 / (n * min(r - 1, c - 1))].
    v = np.sqrt(qui2 / (o.sum() * min(o.shape[0] - 1, o.shape[1] - 1)))
    # Cada célula contribui com (observado - esperado)² / esperado.
    contrib = (o - esperadas) ** 2 / esperadas
    if esperadas.min() < 5:
        raise ValueError("Frequências esperadas inferiores a cinco: revisar pressupostos")
    return {
        "proveniencia": (
            f"Snapshot UCI: {base_parquet.name}; contagens derivadas da base obtida"
            if base_parquet is not None
            else "Tabela da Entrega 3; equivalência com CSV oficial não verificada"
        ),
        "grupos": list(GRUPOS),
        "desfechos": list(COLUNAS),
        "observadas": o.tolist(),
        "esperadas": esperadas.tolist(),
        "contribuicoes": contrib.tolist(),
        "chi2": float(qui2),
        "graus_liberdade": int(gl),
        "p_valor": float(p),
        "v_cramer": float(v),
        "frequencia_esperada_minima": float(esperadas.min()),
        "evasao_sem_bolsa_pct": float(100 * o[0, 0] / o[0].sum()),
        "evasao_com_bolsa_pct": float(100 * o[1, 0] / o[1].sum()),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reproduz o teste Qui-Quadrado da Entrega 3.")
    parser.add_argument(
        "--base", type=Path, default=None,
        help="Snapshot .parquet obtido da UCI; sem opção, usa a tabela agregada da Entrega 3",
    )
    args = parser.parse_args()
    if args.base is not None and args.base.suffix.lower() != ".parquet":
        parser.error("--base aceita snapshots Parquet (.parquet)")
    resultado = calcular(args.base)
    # Mantém resultados históricos; cálculos a partir de snapshots ganham nome próprio.
    destino = (
        BASE / "results" / (args.base.stem + "_resultados.json")
        if args.base is not None else BASE / "results" / "resultados.json"
    )
    destino.write_text(json.dumps(resultado, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"chi2({resultado['graus_liberdade']}) = {resultado['chi2']:.4f}")
    print(f"p = {resultado['p_valor']:.6e}; V = {resultado['v_cramer']:.4f}")
    print(f"Arquivo gerado: {destino}")
