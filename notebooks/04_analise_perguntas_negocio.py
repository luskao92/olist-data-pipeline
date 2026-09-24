# Databricks notebook source
# MAGIC %md
# MAGIC # 04 - Análise: Respostas às 7 perguntas de negócio
# MAGIC
# MAGIC Consulta as tabelas Gold para responder às perguntas definidas em `docs/01-contexto-negocios-e-perguntas.md`.

# COMMAND ----------

from pyspark.sql import functions as F

CATALOGO = "workspace"
SCHEMA_GOLD = "gold"

dim_cliente = spark.table(f"{CATALOGO}.{SCHEMA_GOLD}.dim_cliente")
dim_produto = spark.table(f"{CATALOGO}.{SCHEMA_GOLD}.dim_produto")
dim_vendedor = spark.table(f"{CATALOGO}.{SCHEMA_GOLD}.dim_vendedor")
dim_data = spark.table(f"{CATALOGO}.{SCHEMA_GOLD}.dim_data")
dim_pedido = spark.table(f"{CATALOGO}.{SCHEMA_GOLD}.dim_pedido")
fato_pedido_itens = spark.table(f"{CATALOGO}.{SCHEMA_GOLD}.fato_pedido_itens")
fato_pagamentos = spark.table(f"{CATALOGO}.{SCHEMA_GOLD}.fato_pagamentos")
fato_avaliacoes = spark.table(f"{CATALOGO}.{SCHEMA_GOLD}.fato_avaliacoes")

dim_cliente.createOrReplaceTempView("dim_cliente")
dim_produto.createOrReplaceTempView("dim_produto")
dim_vendedor.createOrReplaceTempView("dim_vendedor")
dim_data.createOrReplaceTempView("dim_data")
dim_pedido.createOrReplaceTempView("dim_pedido")
fato_pedido_itens.createOrReplaceTempView("fato_pedido_itens")
fato_pagamentos.createOrReplaceTempView("fato_pagamentos")
fato_avaliacoes.createOrReplaceTempView("fato_avaliacoes")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Pergunta 1: o atraso na entrega impacta a nota de avaliação?

# COMMAND ----------

pergunta1 = spark.sql("""
SELECT
    CASE
        WHEN p.dias_atraso IS NULL THEN 'sem informacao de entrega'
        WHEN p.dias_atraso <= 0 THEN 'no prazo ou antecipado'
        WHEN p.dias_atraso BETWEEN 1 AND 3 THEN 'atraso leve (1-3 dias)'
        ELSE 'atraso grande (4+ dias)'
    END AS faixa_atraso,
    ROUND(AVG(a.review_score), 2) AS nota_media,
    COUNT(*) AS n_avaliacoes
FROM fato_avaliacoes a
JOIN dim_pedido p ON a.sk_pedido = p.sk_pedido
GROUP BY 1
ORDER BY 2 DESC
""")
display(pergunta1)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Pergunta 2: quais categorias têm maior ticket médio e maior participação na receita?

# COMMAND ----------

pergunta2 = spark.sql("""
SELECT
    pr.product_category_name_english AS categoria,
    ROUND(AVG(fi.price), 2) AS ticket_medio,
    ROUND(SUM(fi.price), 2) AS receita_total,
    ROUND(100.0 * SUM(fi.price) / SUM(SUM(fi.price)) OVER (), 2) AS pct_receita_total,
    COUNT(*) AS n_itens
FROM fato_pedido_itens fi
JOIN dim_produto pr ON fi.sk_produto = pr.sk_produto
GROUP BY 1
ORDER BY receita_total DESC
LIMIT 15
""")
display(pergunta2)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Pergunta 3a: qual estado seria mais indicado para um novo Centro de Distribuição?

# COMMAND ----------

pergunta3a = spark.sql("""
SELECT
    c.customer_state AS estado_cliente,
    COUNT(DISTINCT p.sk_pedido) AS n_pedidos,
    ROUND(AVG(fi.freight_value), 2) AS frete_medio,
    ROUND(AVG(p.dias_atraso), 2) AS atraso_medio_dias
FROM fato_pedido_itens fi
JOIN dim_pedido p ON fi.sk_pedido = p.sk_pedido
JOIN dim_cliente c ON p.sk_cliente = c.sk_cliente
GROUP BY 1
ORDER BY n_pedidos DESC
LIMIT 10
""")
display(pergunta3a)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Pergunta 3b: quais categorias teriam maior demanda no estado identificado acima?
# MAGIC
# MAGIC **Ajuste `ESTADO_ALVO` com o estado escolhido a partir da pergunta 3a antes de rodar esta célula.**

# COMMAND ----------

ESTADO_ALVO = "SP"  # AJUSTAR conforme resultado da pergunta 3a

pergunta3b = spark.sql(f"""
SELECT
    pr.product_category_name_english AS categoria,
    COUNT(*) AS n_itens,
    ROUND(SUM(fi.price), 2) AS receita_total
FROM fato_pedido_itens fi
JOIN dim_pedido p ON fi.sk_pedido = p.sk_pedido
JOIN dim_cliente c ON p.sk_cliente = c.sk_cliente
JOIN dim_produto pr ON fi.sk_produto = pr.sk_produto
WHERE c.customer_state = '{ESTADO_ALVO}'
GROUP BY 1
ORDER BY n_itens DESC
LIMIT 10
""")
display(pergunta3b)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Pergunta 4: forma de pagamento mais usada x número de parcelas x valor

# COMMAND ----------

pergunta4 = spark.sql("""
SELECT
    payment_type,
    COUNT(*) AS n_pagamentos,
    ROUND(AVG(payment_installments), 2) AS parcelas_medias,
    ROUND(AVG(payment_value), 2) AS valor_medio
FROM fato_pagamentos
GROUP BY 1
ORDER BY n_pagamentos DESC
""")
display(pergunta4)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Pergunta 5: existe sazonalidade mensal nas vendas?

# COMMAND ----------

pergunta5 = spark.sql("""
SELECT
    d.ano,
    d.mes,
    d.nome_mes,
    COUNT(DISTINCT fi.sk_pedido) AS n_pedidos,
    ROUND(SUM(fi.price), 2) AS receita_total
FROM fato_pedido_itens fi
JOIN dim_pedido p ON fi.sk_pedido = p.sk_pedido
JOIN dim_data d ON p.data_compra = d.data
GROUP BY 1, 2, 3
ORDER BY 1, 2
""")
display(pergunta5)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Pergunta 6: vendedores com entrega mais rápida recebem avaliações melhores?

# COMMAND ----------

pergunta6 = spark.sql("""
SELECT
    v.seller_id,
    v.seller_state,
    ROUND(AVG(p.dias_atraso), 2) AS atraso_medio_dias,
    ROUND(AVG(a.review_score), 2) AS nota_media,
    COUNT(DISTINCT p.sk_pedido) AS n_pedidos
FROM fato_pedido_itens fi
JOIN dim_vendedor v ON fi.sk_vendedor = v.sk_vendedor
JOIN dim_pedido p ON fi.sk_pedido = p.sk_pedido
JOIN fato_avaliacoes a ON a.sk_pedido = p.sk_pedido
GROUP BY 1, 2
HAVING COUNT(DISTINCT p.sk_pedido) >= 10
ORDER BY nota_media DESC
""")
display(pergunta6)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Pergunta 7: recência e recompra (por customer_unique_id)

# COMMAND ----------

pergunta7_base = spark.sql("""
SELECT
    c.customer_unique_id,
    p.data_compra,
    ROW_NUMBER() OVER (PARTITION BY c.customer_unique_id ORDER BY p.data_compra) AS ordem_compra
FROM dim_pedido p
JOIN dim_cliente c ON p.sk_cliente = c.sk_cliente
""")
pergunta7_base.createOrReplaceTempView("pergunta7_base")

pergunta7_resumo = spark.sql("""
SELECT
    COUNT(DISTINCT customer_unique_id) AS total_clientes,
    COUNT(DISTINCT CASE WHEN ordem_compra = 2 THEN customer_unique_id END) AS clientes_com_recompra,
    ROUND(
        100.0 * COUNT(DISTINCT CASE WHEN ordem_compra = 2 THEN customer_unique_id END)
        / COUNT(DISTINCT customer_unique_id), 2
    ) AS taxa_recompra_pct
FROM pergunta7_base
""")
display(pergunta7_resumo)

# COMMAND ----------

pergunta7_tempo_medio = spark.sql("""
SELECT ROUND(AVG(DATEDIFF(d2.data_compra, d1.data_compra)), 1) AS dias_medios_entre_1a_e_2a_compra
FROM pergunta7_base d1
JOIN pergunta7_base d2
    ON d1.customer_unique_id = d2.customer_unique_id
    AND d1.ordem_compra = 1
    AND d2.ordem_compra = 2
""")
display(pergunta7_tempo_medio)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Resumo executivo (preencher após analisar os resultados acima)
# MAGIC
# MAGIC | # | Pergunta | Resposta / achado principal |
# MAGIC |---|---|---|
# MAGIC | 1 | Atraso x satisfação | _preencher_ |
# MAGIC | 2 | Receita por categoria | _preencher_ |
# MAGIC | 3a | Estado para novo CD | _preencher_ |
# MAGIC | 3b | Categorias no estado escolhido | _preencher_ |
# MAGIC | 4 | Pagamento x parcelas | _preencher_ |
# MAGIC | 5 | Sazonalidade mensal | _preencher_ |
# MAGIC | 6 | Vendedor x avaliação | _preencher_ |
# MAGIC | 7 | Recência/recompra | _preencher_ |
