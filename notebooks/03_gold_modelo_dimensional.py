# Databricks notebook source
# MAGIC %md
# MAGIC # 03 - Gold: Modelo dimensional (Star Schema / Constelação de Fatos)
# MAGIC
# MAGIC Constrói as dimensões e fatos descritos em `docs/02-modelagem-catalogo-dados.md`, a partir das tabelas Silver.

# COMMAND ----------

from pyspark.sql import functions as F
from pyspark.sql.window import Window

CATALOGO = "workspace"
SCHEMA_SILVER = "silver"
SCHEMA_GOLD = "gold"

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOGO}.{SCHEMA_GOLD}")

# COMMAND ----------

# MAGIC %md ## dim_cliente

# COMMAND ----------

customers_silver = spark.table(f"{CATALOGO}.{SCHEMA_SILVER}.customers")

dim_cliente = (
    customers_silver
    .groupBy("customer_unique_id")
    .agg(
        F.first("customer_city").alias("customer_city"),
        F.first("customer_state").alias("customer_state"),
        F.first("customer_zip_code_prefix").alias("customer_zip_code_prefix"),
    )
    .withColumn("sk_cliente", F.row_number().over(Window.orderBy("customer_unique_id")))
    .select("sk_cliente", "customer_unique_id", "customer_city", "customer_state", "customer_zip_code_prefix")
)

dim_cliente.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{CATALOGO}.{SCHEMA_GOLD}.dim_cliente")
print(f"dim_cliente: {dim_cliente.count()} clientes únicos")

# COMMAND ----------

# MAGIC %md ## dim_produto

# COMMAND ----------

products_silver = spark.table(f"{CATALOGO}.{SCHEMA_SILVER}.products")

dim_produto = (
    products_silver
    .withColumn("sk_produto", F.row_number().over(Window.orderBy("product_id")))
    .select(
        "sk_produto",
        "product_id",
        "product_category_name_english",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm",
    )
)

dim_produto.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{CATALOGO}.{SCHEMA_GOLD}.dim_produto")
print(f"dim_produto: {dim_produto.count()} produtos")

# COMMAND ----------

# MAGIC %md ## dim_vendedor

# COMMAND ----------

sellers_silver = spark.table(f"{CATALOGO}.{SCHEMA_SILVER}.sellers")

dim_vendedor = (
    sellers_silver
    .withColumn("sk_vendedor", F.row_number().over(Window.orderBy("seller_id")))
    .select("sk_vendedor", "seller_id", "seller_city", "seller_state")
)

dim_vendedor.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{CATALOGO}.{SCHEMA_GOLD}.dim_vendedor")
print(f"dim_vendedor: {dim_vendedor.count()} vendedores")

# COMMAND ----------

# MAGIC %md ## dim_data

# COMMAND ----------

orders_silver = spark.table(f"{CATALOGO}.{SCHEMA_SILVER}.orders")

datas_min_max = orders_silver.select(
    F.least(
        F.min("order_purchase_timestamp"),
        F.min("order_delivered_customer_date"),
        F.min("order_estimated_delivery_date"),
    ).alias("data_min"),
    F.greatest(
        F.max("order_purchase_timestamp"),
        F.max("order_delivered_customer_date"),
        F.max("order_estimated_delivery_date"),
    ).alias("data_max"),
).first()

data_min = datas_min_max["data_min"].date()
data_max = datas_min_max["data_max"].date()

dim_data = (
    spark.sql(f"SELECT explode(sequence(to_date('{data_min}'), to_date('{data_max}'), interval 1 day)) as data")
    .withColumn("ano", F.year("data"))
    .withColumn("mes", F.month("data"))
    .withColumn("dia", F.dayofmonth("data"))
    .withColumn("nome_mes", F.date_format("data", "MMMM"))
    .withColumn("trimestre", F.quarter("data"))
    .withColumn("dia_da_semana", F.date_format("data", "EEEE"))
    .withColumn("fim_de_semana", F.dayofweek("data").isin([1, 7]))
)

dim_data.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{CATALOGO}.{SCHEMA_GOLD}.dim_data")
print(f"dim_data: {dim_data.count()} dias ({data_min} a {data_max})")

# COMMAND ----------

# MAGIC %md ## dim_pedido

# COMMAND ----------

dim_pedido = (
    orders_silver
    .join(customers_silver.select("customer_id", "customer_unique_id"), on="customer_id", how="left")
    .join(dim_cliente.select("sk_cliente", "customer_unique_id"), on="customer_unique_id", how="left")
    .withColumn("data_compra", F.to_date("order_purchase_timestamp"))
    .withColumn("sk_pedido", F.row_number().over(Window.orderBy("order_id")))
    .select("sk_pedido", "order_id", "sk_cliente", "order_status", "data_compra", "dias_atraso")
)

dim_pedido.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{CATALOGO}.{SCHEMA_GOLD}.dim_pedido")
print(f"dim_pedido: {dim_pedido.count()} pedidos")

# COMMAND ----------

# MAGIC %md ## fato_pedido_itens

# COMMAND ----------

order_items_silver = spark.table(f"{CATALOGO}.{SCHEMA_SILVER}.order_items")

fato_pedido_itens = (
    order_items_silver
    .join(dim_pedido.select("sk_pedido", "order_id"), on="order_id", how="inner")
    .join(dim_produto.select("sk_produto", "product_id"), on="product_id", how="inner")
    .join(dim_vendedor.select("sk_vendedor", "seller_id"), on="seller_id", how="inner")
    .select("sk_pedido", "sk_produto", "sk_vendedor", "order_item_id", "price", "freight_value")
)

fato_pedido_itens.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{CATALOGO}.{SCHEMA_GOLD}.fato_pedido_itens")
print(f"fato_pedido_itens: {fato_pedido_itens.count()} itens")

# COMMAND ----------

# MAGIC %md ## fato_pagamentos

# COMMAND ----------

order_payments_silver = spark.table(f"{CATALOGO}.{SCHEMA_SILVER}.order_payments")

fato_pagamentos = (
    order_payments_silver
    .join(dim_pedido.select("sk_pedido", "order_id"), on="order_id", how="inner")
    .select("sk_pedido", "payment_sequential", "payment_type", "payment_installments", "payment_value")
)

fato_pagamentos.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{CATALOGO}.{SCHEMA_GOLD}.fato_pagamentos")
print(f"fato_pagamentos: {fato_pagamentos.count()} pagamentos")

# COMMAND ----------

# MAGIC %md ## fato_avaliacoes

# COMMAND ----------

order_reviews_silver = spark.table(f"{CATALOGO}.{SCHEMA_SILVER}.order_reviews")

fato_avaliacoes = (
    order_reviews_silver
    .join(dim_pedido.select("sk_pedido", "order_id"), on="order_id", how="inner")
    .select("sk_pedido", "review_score", "dias_resposta")
)

fato_avaliacoes.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{CATALOGO}.{SCHEMA_GOLD}.fato_avaliacoes")
print(f"fato_avaliacoes: {fato_avaliacoes.count()} avaliações")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Evidência final: contagem de todas as tabelas Gold

# COMMAND ----------

for t in ["dim_cliente", "dim_produto", "dim_vendedor", "dim_data", "dim_pedido",
          "fato_pedido_itens", "fato_pagamentos", "fato_avaliacoes"]:
    n = spark.table(f"{CATALOGO}.{SCHEMA_GOLD}.{t}").count()
    print(f"{t}: {n} linhas")
