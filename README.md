# Qui-Quadrado de Pearson: bolsa e situação acadêmica

Repositório de reprodutibilidade da aplicação estatística documentada na **Entrega 3** de André Luiz Pimenta Maia (PPGMCS/Unimontes). Base de referência: **UCI 697 — Predict Students' Dropout and Academic Success**.

## Organização

```text
chi-square-student-dropout/
├── README.md
├── .gitignore
├── requirements.txt
├── data/
│   └── processed/
│       └── tabela_observada_entrega3.csv
├── src/
│   ├── calcular_quiquadrado.py
│   └── conferir_csv_uci.py
├── results/
│   └── resultados.json
└── tests/
    └── test_calculos.py
```

- **data/processed/**: a tabela agregada documentada na Entrega 3, não o arquivo bruto da UCI.
- **src/**: cálculos estatísticos e auditoria do CSV obtido separadamente.
- **results/**: saída da reprodução do teste.
- **tests/**: verificações automatizadas dos resultados esperados.

## Preparar o ambiente no Ubuntu

Requer Python 3.10 ou superior.

```bash
git clone https://github.com/maiandreh/chi-square-student-dropout.git
cd chi-square-student-dropout
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Se o repositório já foi clonado, basta entrar na pasta e executar `git pull`, antes de ativar o ambiente.

## Reproduzir o teste

```bash
python src/calcular_quiquadrado.py
python -m unittest discover -s tests -v
```

A saída será escrita em `results/resultados.json` e inclui frequências observadas/esperadas, contribuição por célula, estatística de Pearson, graus de liberdade, p-valor, V de Cramér e proporções de evasão.

### Frequências utilizadas

| Bolsa | Dropout | Enrolled | Graduate | Total |
|---|---:|---:|---:|---:|
| Sem bolsa | 1.287 | 664 | 1.374 | 3.325 |
| Com bolsa | 134 | 130 | 835 | 1.099 |
| Total | 1.421 | 794 | 2.209 | 4.424 |

Resultados: **χ²(2) = 409,9431; p ≈ 9,59 × 10⁻⁹⁰; V de Cramér = 0,3044**. A menor frequência esperada é cerca de **197,24**.

O teste evidencia associação na tabela examinada, **não causalidade**.

## Obter e conferir os dados oficiais

1. Acesse a página oficial [UCI 697](https://archive.ics.uci.edu/dataset/697/predict+students+dropout+and+academic+success), DOI: **10.24432/C5MC89**.
2. Baixe o conjunto **Predict Students' Dropout and Academic Success** e extraia o CSV.
3. Preserve o arquivo bruto sem alterações, preferencialmente em `data/raw/` (ignorado pelo Git).
4. Compare as seis contagens com a tabela utilizada no trabalho:

```bash
python src/conferir_csv_uci.py data/raw/data.csv
```

Substitua o caminho pelo nome real do CSV extraído, se diferente. O script espera as colunas `Scholarship holder` e `Target`, com delimitador ponto e vírgula. Retorna código de saída 1 diante de divergências e **não modifica o arquivo bruto**.

**Limitação de proveniência:** a tabela utilizada foi recuperada da Entrega 3. A correspondência exata entre a cópia de dados então examinada e o arquivo original da UCI ainda depende dessa conferência. Por esse motivo, não disponibilizamos um CSV bruto presumido como oficial.

## Referências utilizadas

- COCHRAN, W. G. Some methods for strengthening the common χ² tests. *Biometrics*, 1954. DOI: 10.2307/3001616.
- REALINHO, V. et al. Predict Students' Dropout and Academic Success. *UCI Machine Learning Repository*, 2021. DOI: 10.24432/C5MC89.
- ROMERO, S.; LIAO, X. Statistical and machine learning models for predicting university dropout and scholarship impact. *PLOS ONE*, 2025. DOI: 10.1371/journal.pone.0325047.
