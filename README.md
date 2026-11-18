# Qui-Quadrado: bolsa de estudos e situação acadêmica (UCI 697)

Reprodução da aplicação de André Luiz Pimenta Maia, PPGMCS/Unimontes.

## Dados e procedimento

A Entrega 3 registra uma tabela de contingência 2 × 3 com 4.424 estudantes. A análise preserva os desfechos `Dropout`, `Enrolled` e `Graduate`.

| Recebe bolsa? | Dropout | Enrolled | Graduate |
|---|---:|---:|---:|
| Não | 1287 | 664 | 1374 |
| Sim | 134 | 130 | 835 |

**Proveniência:** as contagens foram transcritas da Entrega 3. O teste pode ser reproduzido a partir dessa tabela. A equivalência byte a byte do CSV usado na Entrega 3 com o original da UCI não foi comprovada.

## Obter a base original

1. Acesse o repositório oficial do conjunto: https://archive.ics.uci.edu/dataset/697/predict+students+dropout+and+academic+success
2. Faça o download de **Predict Students' Dropout and Academic Success** (DOI: 10.24432/C5MC89).
3. Extraia o CSV do arquivo baixado e preserve uma cópia sem modificações.
4. Execute a conferência de contagens com `python conferir_csv_uci.py /caminho/para/data.csv`.

Não incluímos uma cópia não verificada do CSV. Se o script indicar divergência, ela deverá ser examinada, não corrigida silenciosamente.

## Reproduzir cálculos

Requisitos: Python 3.10+ e bibliotecas NumPy e SciPy.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python calcular_quiquadrado.py
python conferir_csv_uci.py /caminho/para/data.csv
```

O script de cálculo gera `resultados.json`, com observados, esperados, contribuição de cada célula para a estatística χ², graus de liberdade, p-valor, V de Cramér e taxas de evasão.

## Valores reproduzidos

- χ²(2) = 409,9431;
- p ≈ 9,59 × 10⁻⁹⁰;
- V de Cramér = 0,3044;
- menor frequência esperada ≈ 197,244.

O teste indica associação estatística na tabela analisada. **Não demonstra efeito causal das bolsas** e não resolve sozinho a questão da independência entre estudantes.

## Referências utilizadas no artigo

- COCHRAN, W. G. Some methods for strengthening the common χ² tests. *Biometrics*, 1954. DOI: 10.2307/3001616.
- REALINHO, V. et al. Predict Students’ Dropout and Academic Success. *UCI Machine Learning Repository*, 2021. DOI: 10.24432/C5MC89.
- ROMERO, S.; LIAO, X. Statistical and machine learning models for predicting university dropout and scholarship impact. *PLOS ONE*, 2025. DOI: 10.1371/journal.pone.0325047.
