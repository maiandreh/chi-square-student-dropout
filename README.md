# Materiais de apoio a resumos expandidos — Qui-Quadrado e evasão no ensino superior

Repositório **público de materiais de apoio, dados derivados, scripts e resultados verificáveis** para elaboração de resumos expandidos acadêmicos. Este conjunto de arquivos documenta uma aplicação do teste Qui-Quadrado de Pearson à associação entre recebimento de bolsa e situação acadêmica, usando o conjunto *Predict Students' Dropout and Academic Success* (UCI 697).

**Responsável:** André Luiz Pimenta Maia — PPGMCS/Unimontes.

O repositório é um material de apoio à produção e à conferência de textos científicos. **Não representa uma disciplina, uma atividade avaliativa específica nem a reprodução integral dos modelos de Romero e Liao (2025).** Os scripts documentam uma análise delimitada e seus pressupostos.

## Estrutura

```text
chi-square-student-dropout/
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   ├── processed/
│   │   └── frequencias_observadas_bolsa_situacao.csv    # Contagens históricas
│   └── raw/                                 # Snapshots UCI; ignorados pelo Git
├── src/
│   ├── obter_base_uci.py                    # Download direto, timestamp, Parquet e metadados
│   ├── calcular_quiquadrado.py              # Teste da tabela ou do snapshot
│   └── conferir_csv_uci.py                  # Conferência de CSV manual (legado)
├── results/
│   └── resultados.json                      # Reprodução da tabela histórica
└── tests/
    ├── test_calculos.py
    └── test_snapshots.py
```

## Preparação (Ubuntu / Linux)

Requer Python 3.10+ e conexão com a internet para obter a base pela primeira vez.

```bash
git clone https://github.com/maiandreh/chi-square-student-dropout.git
cd chi-square-student-dropout
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Se o projeto já estiver clonado, execute `git pull origin main` na pasta do projeto. O diretório `.venv` é local e não deve ser versionado.

## Fluxo principal: obter diretamente da UCI (sem CSV manual)

A UCI disponibiliza o cliente Python `ucimlrepo`. O script usa `fetch_ucirepo(id=697)` e guarda todas as 37 colunas em **Parquet**, preservando os nomes originais:

```bash
python src/obter_base_uci.py
```

São criados dois arquivos locais com **carimbo de data e hora UTC da obtenção**:

```text
data/raw/uci697_obtido_YYYYMMDDTHHMMSSZ.parquet
data/raw/uci697_obtido_YYYYMMDDTHHMMSSZ_metadata.json
```

O arquivo de metadados registra: ID e DOI, URL oficial, timestamp UTC, número de linhas/colunas, versões das bibliotecas, nome do snapshot e **SHA-256 do Parquet salvo**. O script exige 4.424 linhas, 37 colunas e as seis contagens esperadas. Se houver divergência, informa o erro em vez de publicar dados incompatíveis com a análise original.

Para executar o teste **diretamente sobre o snapshot Parquet**, use o nome efetivamente gerado:

```bash
python src/calcular_quiquadrado.py --base data/raw/uci697_obtido_YYYYMMDDTHHMMSSZ.parquet
```

O resultado será salvo separadamente em:

```text
results/uci697_obtido_YYYYMMDDTHHMMSSZ_resultados.json
```

**Atenção:** substitua `YYYYMMDDTHHMMSSZ` pelo carimbo presente no arquivo. O timestamp é o **instante da consulta**, não uma data de coleta dos estudantes ou de atualização da UCI. O SHA-256 identifica os bytes da cópia Parquet local — **não é o hash do arquivo CSV original**.

## Reproduzir a análise de referência sem baixar a base

```bash
python src/calcular_quiquadrado.py
python -m unittest discover -s tests -v
```

Esse caminho utiliza apenas a tabela documentada e escreve `results/resultados.json`.

| Bolsa | Dropout | Enrolled | Graduate | Total |
|---|---:|---:|---:|---:|
| Sem bolsa | 1.287 | 664 | 1.374 | 3.325 |
| Com bolsa | 134 | 130 | 835 | 1.099 |
| Total | 1.421 | 794 | 2.209 | 4.424 |

Resultados esperados: **χ²(2) = 409,9431; p ≈ 9,59 × 10⁻⁹⁰; V de Cramér = 0,3044**. A menor frequência esperada é aproximadamente 197,244. Não se trata de prova de efeito causal.

## Alternativa: baixar o CSV manualmente

Se preferir a versão distribuída como arquivo, obtenha-a em:

- [Página oficial UCI 697](https://archive.ics.uci.edu/dataset/697/predict+students+dropout+and+academic+success)
- DOI: **10.24432/C5MC89**.

Extraia o CSV, preserve-o sem edições em `data/raw/` e execute:

```bash
python src/conferir_csv_uci.py data/raw/data.csv
```

A ferramenta de conferência assume ponto e vírgula como delimitador, verifica as variáveis `Scholarship holder` e `Target` e compara todas as seis contagens. Os dados brutos e snapshots ficam ignorados pelo Git, evitando republicação acidental.

## Escolha de formato

- **Parquet:** formato recomendado para os snapshots locais, com preservação de esquema, tipos de dados e leitura eficiente pelo pandas.
- **CSV:** formato de intercâmbio e auditoria; continua disponível no repositório da UCI.
- **JSON:** utilizado apenas para os resultados e os metadados; não para os 4.424 registros tabulares.

## Limitação de proveniência

A tabela agregada corresponde às frequências previamente documentadas em uma análise exploratória, elaborada a partir de uma cópia pública obtida anteriormente. Uma nova consulta à UCI que produza as mesmas seis contagens **não comprova a identidade byte a byte da cópia antiga com a fonte primária**. Essa distinção é mantida no código e na documentação.

## Referências

- COCHRAN, W. G. Some methods for strengthening the common χ² tests. *Biometrics*, 1954. DOI: 10.2307/3001616.
- REALINHO, V. et al. Predict Students' Dropout and Academic Success. *UCI Machine Learning Repository*, 2021. DOI: 10.24432/C5MC89.
- ROMERO, S.; LIAO, X. Statistical and machine learning models for predicting university dropout and scholarship impact. *PLOS ONE*, 2025. DOI: 10.1371/journal.pone.0325047.
