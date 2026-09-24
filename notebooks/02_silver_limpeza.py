# Databricks notebook source
# MAGIC %md
# MAGIC # 02 - Silver: Limpeza, tipagem e deduplicação
# MAGIC
# MAGIC Lê as tabelas Bronze, aplica tratamentos de qualidade de dados (completude, consistência, unicidade,
# MAGIC acurácia) e grava como tabelas Delta na camada Silver.

# COMMAND ----------

from pyspark.sql import functions as F

CATALOGO = "workspace"
SCHEMA_BRONZE = "bronze"
SCHEMA_SILVER = "silver"

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOGO}.{SCHEMA_SILVER}")

# COMMAND ----------

# MAGIC %md ## customers

# COMMAND ----------

customers_bronze = spark.table(f"{CATALOGO}.{SCHEMA_BRONZE}.customers")

customers_silver = (
    customers_bronze
    .withColumn("customer_city", F.lower(F.trim(F.col("customer_city"))))
    .withColumn("customer_state", F.upper(F.trim(F.col("customer_state"))))
    .dropDuplicates(["customer_id"])
)

# checagem de completude
n_nulos = customers_silver.filter(F.col("customer_unique_id").isNull()).count()
print(f"customers: {n_nulos} linhas com customer_unique_id nulo (esperado: 0)")

customers_silver.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{CATALOGO}.{SCHEMA_SILVER}.customers")

# COMMAND ----------

# MAGIC %md ## orders

# COMMAND ----------

orders_bronze = spark.table(f"{CATALOGO}.{SCHEMA_BRONZE}.orders")

orders_silver = (
    orders_bronze
    .withColumn("order_purchase_timestamp", F.to_timestamp("order_purchase_timestamp"))
    .withColumn("order_approved_at", F.to_timestamp("order_approved_at"))
    .withColumn("order_delivered_carrier_date", F.to_timestamp("order_delivered_carrier_date"))
    .withColumn("order_delivered_customer_date", F.to_timestamp("order_delivered_customer_date"))
    .withColumn("order_estimated_delivery_date", F.to_timestamp("order_estimated_delivery_date"))
    .withColumn(
        "dias_atraso",
        F.datediff("order_delivered_customer_date", "order_estimated_delivery_date"),
    )
    .dropDuplicates(["order_id"])
)

# checagem de acurácia: status válidos
status_validos = ["delivered", "shipped", "canceled", "unavailable", "invoiced", "processing", "created", "approved"]
status_invalidos = orders_silver.filter(~F.col("order_status").isin(status_validos)).count()
print(f"orders: {status_invalidos} linhas com order_status fora do domínio esperado")

orders_silver.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{CATALOGO}.{SCHEMA_SILVER}.orders")

# COMMAND ----------

# MAGIC %md ## products + category_translation

# COMMAND ----------

products_bronze = spark.table(f"{CATALOGO}.{SCHEMA_BRONZE}.products")
translation_bronze = spark.table(f"{CATALOGO}.{SCHEMA_BRONZE}.category_translation")

# corrige eventual BOM no nome da coluna de origem
for c in translation_bronze.columns:
    if c.startswith("﻿"):
        translation_bronze = translation_bronze.withColumnRenamed(c, c.replace("﻿", ""))

products_silver = (
    products_bronze
    .join(translation_bronze, on="product_category_name", how="left")
    .withColumn(
        "product_category_name_english",
        F.coalesce(F.col("product_category_name_english"), F.lit("categoria_nao_informada")),
    )
    .dropDuplicates(["product_id"])
)

pct_sem_categoria = (
    products_silver.filter(F.col("product_category_name_english") == "categoria_nao_informada").count()
    / products_silver.count()
    * 100
)
print(f"products: {pct_sem_categoria:.2f}% dos produtos sem categoria original")

products_silver.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{CATALOGO}.{SCHEMA_SILVER}.products")

# COMMAND ----------

# MAGIC %md ## sellers

# COMMAND ----------

sellers_bronze = spark.table(f"{CATALOGO}.{SCHEMA_BRONZE}.sellers")

sellers_silver = (
    sellers_bronze
    .withColumn("seller_city", F.lower(F.trim(F.col("seller_city"))))
    .withColumn("seller_state", F.upper(F.trim(F.col("seller_state"))))
    .dropDuplicates(["seller_id"])
)

sellers_silver.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{CATALOGO}.{SCHEMA_SILVER}.sellers")

# COMMAND ----------

# MAGIC %md ## order_items

# COMMAND ----------

order_items_bronze = spark.table(f"{CATALOGO}.{SCHEMA_BRONZE}.order_items")

order_items_silver = (
    order_items_bronze
    .withColumn("price", F.col("price").cast("decimal(10,2)"))
    .withColumn("freight_value", F.col("freight_value").cast("decimal(10,2)"))
    .withColumn("shipping_limit_date", F.to_timestamp("shipping_limit_date"))
)

# checagem de outliers simples (preço muito acima da média)
stats = order_items_silver.select(F.mean("price").alias("media"), F.stddev("price").alias("dp")).first()
limite_outlier = stats["media"] + 3 * stats["dp"]
n_outliers = order_items_silver.filter(F.col("price") > limite_outlier).count()
print(f"order_items: {n_outliers} itens com price acima de média+3dp (limite={limite_outlier:.2f})")

order_items_silver.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{CATALOGO}.{SCHEMA_SILVER}.order_items")

# COMMAND ----------

# MAGIC %md ## order_payments

# COMMAND ----------

order_payments_bronze = spark.table(f"{CATALOGO}.{SCHEMA_BRONZE}.order_payments")

order_payments_silver = (
    order_payments_bronze
    .withColumn("payment_value", F.col("payment_value").cast("decimal(10,2)"))
    .filter(F.col("payment_installments") >= 0)
)

order_payments_silver.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{CATALOGO}.{SCHEMA_SILVER}.order_payments")

# COMMAND ----------

# MAGIC %md ## order_reviews

# COMMAND ----------

order_reviews_bronze = spark.table(f"{CATALOGO}.{SCHEMA_BRONZE}.order_reviews")

order_reviews_silver = (
    order_reviews_bronze
    .withColumn("review_creation_date", F.to_timestamp("review_creation_date"))
    .withColumn("review_answer_timestamp", F.to_timestamp("review_answer_timestamp"))
    .withColumn("dias_resposta", F.datediff("review_answer_timestamp", "review_creation_date"))
    .dropDuplicates(["review_id"])
    .filter(F.col("review_score").between(1, 5))
)

order_reviews_silver.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{CATALOGO}.{SCHEMA_SILVER}.order_reviews")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Resumo de linhas por tabela (evidência para o relatório)

# COMMAND ----------

for t in ["customers", "orders", "products", "sellers", "order_items", "order_payments", "order_reviews"]:
    n = spark.table(f"{CATALOGO}.{SCHEMA_SILVER}.{t}").count()
    print(f"{t}: {n} linhas")
