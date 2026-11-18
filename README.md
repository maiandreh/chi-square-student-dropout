# Chi-Square Student Dropout

Código, dados agregados e resultados para analisar a associação entre o recebimento de bolsa de estudos e a situação acadêmica de estudantes do ensino superior, com o teste Qui-Quadrado de independência de Pearson.

O repositório utiliza o conjunto [Predict Students' Dropout and Academic Success (UCI 697)](https://archive.ics.uci.edu/dataset/697/predict+students+dropout+and+academic+success), com 4.424 registros. A análise considera as categorias `Dropout`, `Enrolled` e `Graduate`, sem atribuir causalidade às associações observadas.

## Estrutura

```text
chi-square-student-dropout/
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   ├── processed/
│   │   └── frequencias_observadas_bolsa_situacao.csv
│   └── raw/                       # Snapshots locais, não versionados
├── src/
│   ├── obter_base_uci.py         # Obtém os dados diretamente da UCI
│   ├── calcular_quiquadrado.py   # Executa o teste de independência
│   └── conferir_csv_uci.py       # Confere um CSV baixado manualmente
├── results/
│   └── resultados.json           # Resultado reproduzido da tabela agregada
└── tests/
    ├── test_calculos.py
    └── test_snapshots.py
```

## Requisitos

- Python 3.10 ou superior; versões 3.11 ou 3.12 são recomendadas.
- Git, para clonar e atualizar o repositório.
- Conexão com a internet para instalar dependências e recuperar a base.

## Instalação

### Linux (Bash)

```bash
git clone https://github.com/maiandreh/chi-square-student-dropout.git
cd chi-square-student-dropout
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### Windows (PowerShell)

```powershell
git clone https://github.com/maiandreh/chi-square-student-dropout.git
cd chi-square-student-dropout
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Se a ativação for bloqueada, use o interpretador do ambiente diretamente, sem alterar a política de execução do Windows:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe src\calcular_quiquadrado.py
```

Se `py` não estiver disponível, utilize `python -m venv .venv` após instalar o Python.

## Como usar

### 1. Executar a análise com as frequências disponíveis

```bash
python src/calcular_quiquadrado.py
```

Esse comando utiliza `data/processed/frequencias_observadas_bolsa_situacao.csv` e atualiza `results/resultados.json`. Não requer download da base completa.

### 2. Obter a base diretamente da UCI

```bash
python src/obter_base_uci.py
```

A recuperação utiliza `ucimlrepo.fetch_ucirepo(id=697)` e salva um snapshot local em Parquet, acompanhado de metadados:

```text
data/raw/uci697_obtido_YYYYMMDDTHHMMSSZ.parquet
data/raw/uci697_obtido_YYYYMMDDTHHMMSSZ_metadata.json
```

O carimbo identifica a data e hora UTC da obtenção, **não** a data de coleta original. Os metadados contêm identificador da fonte, DOI, dimensões, versões de bibliotecas e SHA-256 do arquivo Parquet.

Para analisar o snapshot, substitua o nome abaixo pelo arquivo gerado:

```bash
python src/calcular_quiquadrado.py --base data/raw/uci697_obtido_YYYYMMDDTHHMMSSZ.parquet
```

A saída correspondente será salva em `results/uci697_obtido_YYYYMMDDTHHMMSSZ_resultados.json`.

### 3. Conferir um CSV obtido manualmente (opcional)

Baixe o conjunto na [página oficial da UCI](https://archive.ics.uci.edu/dataset/697/predict+students+dropout+and+academic+success), extraia o CSV e coloque-o em `data/raw/`. Depois execute:

```bash
python src/conferir_csv_uci.py data/raw/data.csv
```

O script compara as seis frequências observadas, sem modificar o arquivo original. Ajuste o caminho caso o arquivo tenha outro nome.

### 4. Executar os testes

```bash
python -m unittest discover -s tests -v
```

Os mesmos comandos Python funcionam no Linux e no Windows quando o ambiente virtual está ativado. Para atualizar uma cópia já clonada, execute `git pull origin main`.

## Resultados de referência

| Bolsa | Dropout | Enrolled | Graduate | Total |
|---|---:|---:|---:|---:|
| Sem bolsa | 1.287 | 664 | 1.374 | 3.325 |
| Com bolsa | 134 | 130 | 835 | 1.099 |
| Total | 1.421 | 794 | 2.209 | 4.424 |

- **χ²(2):** 409,9431
- **p-valor:** aproximadamente 9,59 × 10⁻⁹⁰
- **V de Cramér:** 0,3044
- **Menor frequência esperada:** aproximadamente 197,244

As estatísticas evidenciam associação na tabela analisada, não uma relação causal.

## Dados e reprodutibilidade

A tabela agregada foi produzida a partir de uma cópia pública dos dados. O repositório inclui as contagens e os scripts necessários à reprodução das estatísticas. O fluxo de obtenção direta permite comparar os resultados com uma nova recuperação da UCI, mas contagens coincidentes não comprovam identidade byte a byte entre cópias de momentos diferentes.

O conjunto completo de registros não é versionado: `data/raw/` está excluído pelo `.gitignore`. Parquet é utilizado nos snapshots, CSV nas frequências agregadas e JSON nos resultados e metadados.

## Fonte, atribuição e licença dos dados

- **Conjunto:** Realinho, V. et al. *Predict Students' Dropout and Academic Success*. UCI Machine Learning Repository, 2021. DOI: [10.24432/C5MC89](https://doi.org/10.24432/C5MC89).
- **Licença da base:** [Creative Commons Attribution 4.0 (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).
- **Artigo relacionado:** Romero, S.; Liao, X. *Statistical and machine learning models for predicting university dropout and scholarship impact*. PLOS ONE, 2025. DOI: [10.1371/journal.pone.0325047](https://doi.org/10.1371/journal.pone.0325047).
- **Referência metodológica:** Cochran, W. G. *Some methods for strengthening the common χ² tests*. Biometrics, 1954. DOI: [10.2307/3001616](https://doi.org/10.2307/3001616).

A licença CC BY 4.0 corresponde aos dados da UCI e não define automaticamente a licença dos scripts deste repositório.
