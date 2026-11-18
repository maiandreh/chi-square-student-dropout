"""Testa o fluxo Parquet local sem fazer requisições à UCI.

Executar com: python -m unittest discover -s tests -v
"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from calcular_quiquadrado import calcular
from obter_base_uci import count_outcomes, EXPECTED


class TestSnapshotLocal(unittest.TestCase):
    def test_snapshot_reproduz_tabela(self):
        # Apenas sintetiza as contagens já publicadas; não substitui dados originais.
        linhas = []
        for (bolsa, situacao), quantidade in EXPECTED.items():
            linhas.extend(
                {"Scholarship holder": int(bolsa), "Target": situacao}
                for _ in range(quantidade)
            )
        df = pd.DataFrame(linhas)
        self.assertEqual(count_outcomes(df), EXPECTED)
        with tempfile.TemporaryDirectory() as pasta:
            arquivo = Path(pasta) / "uci697_obtido_teste.parquet"
            df.to_parquet(arquivo, index=False)
            resultado = calcular(arquivo)
        self.assertAlmostEqual(resultado["chi2"], 409.94305544699375, places=8)
        self.assertAlmostEqual(resultado["v_cramer"], 0.30440670047871277, places=8)

    def test_categoria_invalida_rejeitada(self):
        # Categorias inventadas ou ausências nunca devem passar silenciosamente.
        df = pd.DataFrame({
            "Scholarship holder": [0, 2],
            "Target": ["Dropout", "Graduate"],
        })
        with self.assertRaises(ValueError):
            count_outcomes(df)


if __name__ == "__main__":
    unittest.main()
