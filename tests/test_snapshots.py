"""Testes locais do fluxo de aquisição e validação (sem acesso à rede)."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from calcular_quiquadrado import calcular
from obter_base_uci import salvar_snapshot
from validar_base_uci import frequencias, referencia, validar


def dataset_sintetico():
    """Replica somente a tabela de frequências; não é cópia da UCI."""
    linhas = []
    for (bolsa, situacao), n in referencia().items():
        linhas.extend(
            {"Scholarship holder": int(bolsa), "Target": situacao}
            for _ in range(n)
        )
    return pd.DataFrame(linhas)


class TestSnapshotLocal(unittest.TestCase):
    def test_snapshot_e_metadados(self):
        df = dataset_sintetico()
        self.assertEqual(frequencias(df), referencia())
        with tempfile.TemporaryDirectory() as pasta:
            parquet, manifesto = salvar_snapshot(df, Path(pasta))
            self.assertTrue(parquet.exists())
            m = json.loads(manifesto.read_text(encoding="utf-8"))
            self.assertEqual(m["dataset_id"], 697)
            self.assertEqual(m["snapshot_file"], parquet.name)
            self.assertEqual(m["rows"], 4424)
            self.assertEqual(len(m["sha256_parquet"]), 64)
            self.assertEqual(m["validation"], "Pendente: executar src/validar_base_uci.py")
            self.assertEqual(validar(pd.read_parquet(parquet))["status"], "compativel")
            resultado = calcular(parquet)
            self.assertAlmostEqual(resultado["chi2"], 409.94305544699375, places=8)

    def test_aquisicao_nao_bloqueia_base_divergente(self):
        df = pd.DataFrame({
            "Scholarship holder": [0, 1],
            "Target": ["Dropout", "Graduate"],
        })
        with tempfile.TemporaryDirectory() as pasta:
            parquet, metadata = salvar_snapshot(df, Path(pasta))
            self.assertTrue(parquet.is_file())
            self.assertTrue(metadata.is_file())
            relatorio = validar(pd.read_parquet(parquet))
            self.assertEqual(relatorio["status"], "divergente")
            self.assertTrue(relatorio["divergencias"])

    def test_categoria_invalida_nao_e_ocultada(self):
        df = pd.DataFrame({
            "Scholarship holder": [0, 2],
            "Target": ["Dropout", "Graduate"],
        })
        self.assertEqual(validar(df)["status"], "divergente")
        self.assertIn(("2", "Graduate"), frequencias(df))

    def test_rejeita_dados_vazios(self):
        with tempfile.TemporaryDirectory() as pasta:
            with self.assertRaises(ValueError):
                salvar_snapshot(pd.DataFrame(), Path(pasta))

    def test_validador_sem_acesso_a_rede(self):
        self.assertEqual(validar(dataset_sintetico())["status"], "compativel")


if __name__ == "__main__":
    unittest.main()
