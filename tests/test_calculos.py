"""Testes de regressão dos resultados da tabela publicada na Entrega 3.

Executar da raiz: python -m unittest discover -s tests -v
"""
import sys
import unittest
from pathlib import Path

# A análise é um script simples, sem exigir empacotamento como biblioteca.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from calcular_quiquadrado import carregar_observados, calcular


class TestQuiQuadrado(unittest.TestCase):
    """Asserções sobre os valores da aplicação já documentada."""

    def test_frequencias(self):
        o = carregar_observados()
        self.assertEqual(o.shape, (2, 3))
        self.assertEqual(o.sum(), 4424)
        self.assertEqual(o.sum(axis=0).tolist(), [1421, 794, 2209])

    def test_estatisticas(self):
        r = calcular()
        self.assertEqual(r["graus_liberdade"], 2)
        self.assertAlmostEqual(r["chi2"], 409.94305544699375, places=8)
        self.assertAlmostEqual(r["v_cramer"], 0.30440670047871277, places=8)
        self.assertAlmostEqual(r["p_valor"], 9.593930375514133e-90, delta=1e-96)

    def test_pressuposto_contagens_e_contribuicoes(self):
        r = calcular()
        self.assertGreater(r["frequencia_esperada_minima"], 5)
        self.assertAlmostEqual(
            sum(sum(linha) for linha in r["contribuicoes"]),
            r["chi2"], places=10
        )


if __name__ == "__main__":
    unittest.main()
