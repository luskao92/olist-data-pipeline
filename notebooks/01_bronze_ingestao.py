# Databricks notebook source
# MAGIC %md
# MAGIC # 01 - Bronze: Ingestão dos dados brutos (Olist)
# MAGIC
# MAGIC Lê os CSVs originais do Olist (sem nenhuma transformação) e grava como tabelas Delta na camada Bronze.
# MAGIC Convenção de schema: `bronze.<nome_tabela>`.
# MAGIC
# MAGIC **Pré-requisito:** os 9 arquivos CSV do dataset Olist devem estar disponíveis. Neste notebook, assumimos que
# MAGIC eles foram enviados para um Volume do Unity Catalog (recomendado) ou para DBFS.
# MAGIC Ajuste `CAMINHO_ORIGEM` conforme onde você subiu os arquivos no Databricks.

# COMMAND ----------

CAMINHO_ORIGEM = "/Volumes/workspace/default/olist_raw"  # AJUSTAR conforme o volume criado no seu workspace
CATALOGO = "workspace"
SCHEMA_BRONZE = "bronze"

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOGO}.{SCHEMA_BRONZE}")

# COMMAND ----------

ARQUIVOS = {
    "customers": "olist_customers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
    "order_reviews": "olist_order_reviews_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "category_translation": "product_category_name_translation.csv",
}

# COMMAND ----------

for nome_tabela, nome_arquivo in ARQUIVOS.items():
    caminho = f"{CAMINHO_ORIGEM}/{nome_arquivo}"
    df = (
        spark.read.format("csv")
        .option("header", "true")
        .option("inferSchema", "true")
        .option("encoding", "UTF-8")
        .option("multiLine", "true")   # review_comment_message tem quebras de linha dentro de campos
        .option("quote", '"')
        .option("escape", '"')
        .load(caminho)
    )
    tabela_destino = f"{CATALOGO}.{SCHEMA_BRONZE}.{nome_tabela}"
    df.write.format("delta").mode("overwrite").saveAsTable(tabela_destino)
    print(f"OK: {tabela_destino} ({df.count()} linhas, {len(df.columns)} colunas)")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Evidência de carga (para print no relatório final)

# COMMAND ----------

for nome_tabela in ARQUIVOS:
    display(spark.sql(f"SELECT * FROM {CATALOGO}.{SCHEMA_BRONZE}.{nome_tabela} LIMIT 5"))
