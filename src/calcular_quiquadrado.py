"""Reproduz o teste de Pearson a partir da tabela publicada na Entrega 3.

Este cálculo não constitui nova extração nem autenticação do CSV oficial.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
from scipy.stats import chi2_contingency

BASE = Path(__file__).resolve().parent.parent
COLUNAS = ("dropout", "enrolled", "graduate")
GRUPOS = ("sem_bolsa", "com_bolsa")


def carregar_observados() -> np.ndarray:
    """Lê frequências inteiras; confere estrutura, ordem das linhas e total."""
    with (BASE / "data" / "processed" / "tabela_observada_entrega3.csv").open(encoding="utf-8", newline="") as arquivo:
        linhas = list(csv.DictReader(arquivo))
    if [linha["bolsa"] for linha in linhas] != list(GRUPOS):
        raise ValueError("Grupos diferentes dos registrados na Entrega 3")
    observados = np.array([[int(linha[c]) for c in COLUNAS] for linha in linhas], dtype=int)
    if observados.shape != (2, 3) or (observados < 0).any() or observados.sum() != 4424:
        raise ValueError("Tabela inconsistente com a Entrega 3")
    return observados


def calcular() -> dict:
    """Calcula esperados, contribuições, estatística, p-valor e V de Cramér."""
    o = carregar_observados()
    # A correção de Yates não se aplica à presente tabela 2 × 3.
    qui2, p, gl, esperadas = chi2_contingency(o, correction=False)
    # V = raiz[qui2 / (n * min(r - 1, c - 1))].
    v = np.sqrt(qui2 / (o.sum() * min(o.shape[0] - 1, o.shape[1] - 1)))
    # Cada célula contribui com (observado - esperado)² / esperado.
    contrib = (o - esperadas) ** 2 / esperadas
    if esperadas.min() < 5:
        raise ValueError("Frequências esperadas inferiores a cinco: revisar pressupostos")
    return {
        "proveniencia": "Tabela da Entrega 3; equivalência com CSV oficial não verificada",
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
    resultado = calcular()
    destino = BASE / "results" / "resultados.json"
    destino.write_text(json.dumps(resultado, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"chi2({resultado['graus_liberdade']}) = {resultado['chi2']:.4f}")
    print(f"p = {resultado['p_valor']:.6e}; V = {resultado['v_cramer']:.4f}")
    print(f"Arquivo gerado: {destino}")
