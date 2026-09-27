# Carga dos Dados (Etapa 4.2)

## Como foi feita a coleta

1. Os 9 arquivos CSV do Olist Brazilian E-commerce Public Dataset foram baixados manualmente do Kaggle (https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce), após verificação da licença CC BY-NC-SA 4.0 (uso não comercial/acadêmico permitido, com atribuição).
2. Os arquivos foram enviados para um **Volume do Unity Catalog** no Databricks (`/Volumes/workspace/default/olist_raw`), via upload manual pela interface do Databricks (Catalog → Create Volume → Upload). Essa etapa não foi automatizada porque é uma ação pontual de configuração do ambiente, feita uma única vez.
3. Os dados **não foram versionados no GitHub** — apenas o código que os processa. O caminho `data/raw/` está listado no `.gitignore` do repositório, conforme permitido pelo enunciado ("Não é necessário a disponibilização dos dados").

## Como os dados sobem para a plataforma de nuvem

A leitura dos CSVs para dentro do Databricks (camada Bronze) é feita via script, documentado e versionado no GitHub:

- **Script**: [`notebooks/01_bronze_ingestao.py`](../notebooks/01_bronze_ingestao.py)
- O notebook lê cada um dos 9 CSVs do Volume, com tratamento de encoding UTF-8 e de campos multilinha entre aspas (necessário porque a coluna `review_comment_message` contém quebras de linha dentro do texto, o que inicialmente quebrava o parsing — ver `docs/03-qualidade-de-dados.md`), e grava cada um como uma tabela Delta no schema `bronze` do Unity Catalog.
- Evidência de execução: ver `evidencias/bronze-execucao.png`.
