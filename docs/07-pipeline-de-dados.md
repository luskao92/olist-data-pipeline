# Pipeline de Dados (Etapa 4.4)

## Como o pipeline foi organizado

O pipeline ETL foi **ramificado em notebooks separados, um por camada da arquitetura medalhão**, em vez de um único notebook monolítico. Essa escolha isola cada responsabilidade (ingestão, limpeza, modelagem, análise), facilita reexecução independente de uma camada quando algo muda, e deixa o erro mais fácil de localizar durante o desenvolvimento (foi, na prática, o que permitiu depurar rapidamente os problemas de parsing de CSV e de schema do Delta Lake relatados em `docs/03-qualidade-de-dados.md`).

| Notebook | Camada | O que faz |
|---|---|---|
| [`notebooks/01_bronze_ingestao.py`](../notebooks/01_bronze_ingestao.py) | Bronze | Lê os 9 CSVs brutos do Volume do Unity Catalog e grava cada um como tabela Delta em `bronze.*`, sem transformação de conteúdo (apenas tratamento de encoding e de campos multilinha necessário para o parsing correto do CSV). |
| [`notebooks/02_silver_limpeza.py`](../notebooks/02_silver_limpeza.py) | Silver | Lê as tabelas Bronze, aplica tipagem, padronização de texto, deduplicação e as checagens de qualidade documentadas em `docs/03-qualidade-de-dados.md`; grava em `silver.*`. |
| [`notebooks/03_gold_modelo_dimensional.py`](../notebooks/03_gold_modelo_dimensional.py) | Gold | Lê as tabelas Silver e constrói o modelo dimensional (5 dimensões + 3 fatos) descrito em `docs/02-modelagem-catalogo-dados.md`, com geração de surrogate keys; grava em `gold.*`. |
| [`notebooks/04_analise_perguntas_negocio.py`](../notebooks/04_analise_perguntas_negocio.py) | Análise | Consulta as tabelas Gold via SQL para responder às 7 perguntas de negócio; resultados discutidos em `docs/04-analise-resultados.md`. |

Execução: os notebooks são rodados manualmente, em sequência (01 → 02 → 03 → 04), diretamente no Databricks, via Databricks Repos sincronizado com este repositório GitHub. Cada tabela é gravada como Delta table no Unity Catalog (`saveAsTable`, `mode("overwrite")`, com `overwriteSchema=true` quando o schema muda entre execuções).

## Evidência de persistência das tabelas

As capturas abaixo evidenciam a execução de cada notebook e a persistência das tabelas resultantes no Unity Catalog:

- Bronze: [`evidencias/Evidencia_01_Notebook_Bronze.jpg`](../evidencias/Evidencia_01_Notebook_Bronze.jpg)
- Silver: [`evidencias/Evidencia_02_Notebook_Prata.jpg`](../evidencias/Evidencia_02_Notebook_Prata.jpg)
- Gold: [`evidencias/Evidencia_03_Notebook_Ouro.jpg`](../evidencias/Evidencia_03_Notebook_Ouro.jpg)
- Catálogo (schemas `bronze`/`silver`/`gold` no Unity Catalog): [`evidencias/Evidencia_04_Catalogos_Databricks.jpg`](../evidencias/Evidencia_04_Catalogos_Databricks.jpg)
