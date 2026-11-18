"""Compara a tabela da Entrega 3 ao CSV baixado da UCI.

Uso: python conferir_csv_uci.py /caminho/para/data.csv
Não altera o arquivo original. Uma divergência provoca código de saída 1.
"""
from __future__ import annotations

import csv
import sys
from collections import Counter
from pathlib import Path

ESPERADO = {
    ("0", "Dropout"): 1287,
    ("0", "Enrolled"): 664,
    ("0", "Graduate"): 1374,
    ("1", "Dropout"): 134,
    ("1", "Enrolled"): 130,
    ("1", "Graduate"): 835,
}


def conferir(caminho: Path) -> bool:
    """Confere todas as seis células e não tolera categorias inesperadas."""
    with caminho.open(encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.DictReader(arquivo, delimiter=";")
        if leitor.fieldnames is None:
            raise ValueError("CSV vazio")
        # Alguns arquivos trazem espaços ou aspas incidentais nos cabeçalhos.
        leitor.fieldnames = [nome.strip().strip('"') for nome in leitor.fieldnames]
        if not {"Scholarship holder", "Target"}.issubset(leitor.fieldnames):
            raise ValueError("O CSV não contém Scholarship holder e Target")
        contagens = Counter((linha["Scholarship holder"].strip(), linha["Target"].strip()) for linha in leitor)
    # Não usar apenas subconjunto das seis células: categorias extras também são erro.
    coincide = dict(contagens) == ESPERADO
    for (bolsa, desfecho), total in ESPERADO.items():
        print(f"{bolsa}/{desfecho}: arquivo={contagens.get((bolsa, desfecho), 0)}; entrega={total}")
    print("COINCIDE" if coincide else "DIVERGÊNCIA — examinar a fonte")
    return coincide


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Uso: python conferir_csv_uci.py /caminho/para/data.csv")
    raise SystemExit(0 if conferir(Path(sys.argv[1])) else 1)
