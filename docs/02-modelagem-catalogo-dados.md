# Modelagem e Catálogo de Dados (Etapa 3 e 4.3)

## 1. Visão geral do modelo

O modelo escolhido é uma **constelação de fatos** (fact constellation): três tabelas fato, com grãos diferentes, compartilhando cinco dimensões comuns.

```
                         dim_data
                             │
        dim_cliente ── dim_pedido ── dim_produto
                        │      │
           fato_pedido_itens   fato_pagamentos
                        │
                 fato_avaliacoes

        dim_vendedor ──┘ (referenciada por fato_pedido_itens)
```

- **fato_pedido_itens** — grão: 1 linha por item de pedido. Referencia dim_pedido, dim_produto, dim_vendedor, dim_data.
- **fato_pagamentos** — grão: 1 linha por forma de pagamento usada em um pedido. Referencia dim_pedido, dim_data.
- **fato_avaliacoes** — grão: 1 linha por avaliação (review) de pedido. Referencia dim_pedido, dim_data.
- **dim_pedido** — 1 linha por pedido; referencia dim_cliente e dim_data (data da compra).

Camadas: **Bronze** (CSV cru, tipos como veio do Kaggle) → **Silver** (tipado, limpo, deduplicado, nomes padronizados) → **Gold** (modelo dimensional acima, pronto para consulta e para as perguntas de negócio).

Todas as tabelas Gold são gravadas como tabelas **Delta** no Unity Catalog do Databricks, o que cumpre o requisito de Catálogo de Dados exigido no enunciado (Unity Catalog registra schema, tipos e permite consulta de linhagem nativamente).

---

## 2. Dimensões

### 2.1 dim_cliente

| Coluna | Tipo | Domínio de valores | Descrição |
|---|---|---|---|
| sk_cliente | BIGINT | sequencial, não nulo, único | Chave substituta (surrogate key) técnica |
| customer_unique_id | STRING | 32 caracteres hexadecimais | Identificador estável da pessoa (chave de negócio) |
| customer_city | STRING | nomes de cidade em minúsculo | Cidade do cliente |
| customer_state | STRING | 27 UFs do Brasil (sigla, ex. SP, RJ) | Estado do cliente |
| customer_zip_code_prefix | INT | 5 dígitos (prefixo de CEP) | Prefixo do CEP |

**Linhagem:** `data/raw/olist_customers_dataset.csv` → Bronze (`bronze.customers`) → Silver: `dropDuplicates` por `customer_unique_id`, padronização de texto (lower/trim) → Gold: `gold.dim_cliente` (adiciona `sk_cliente`).

**Nota de qualidade:** um mesmo `customer_unique_id` pode ter mais de um `customer_id` (um por pedido); a dimensão deduplica para 1 linha por pessoa, usando a primeira ocorrência de cidade/estado (premissa: cliente não muda de endereço com frequência no período do dataset).

### 2.2 dim_produto

| Coluna | Tipo | Domínio de valores | Descrição |
|---|---|---|---|
| sk_produto | BIGINT | sequencial, não nulo, único | Chave substituta |
| product_id | STRING | 32 caracteres hexadecimais | Chave de negócio do produto |
| product_category_name_english | STRING | ~71 categorias (ou "categoria_nao_informada") | Categoria do produto, traduzida para inglês |
| product_weight_g | INT | ≥ 0, pode ser nulo | Peso do produto em gramas |
| product_length_cm / height_cm / width_cm | INT | ≥ 0, pode ser nulo | Dimensões físicas do produto |

**Linhagem:** `olist_products_dataset.csv` + `product_category_name_translation.csv` → Bronze → Silver: join por `product_category_name`, tratamento de BOM (`﻿`) no cabeçalho da tabela de tradução, produtos sem categoria marcados como `categoria_nao_informada` → Gold: `gold.dim_produto`.

**Nota de qualidade:** ~1,85% dos produtos no dataset original têm `product_category_name` nulo — decisão: manter a linha e marcar categoria como "não informada", em vez de descartar (evita perda de receita nas agregações da pergunta 2).

### 2.3 dim_vendedor

| Coluna | Tipo | Domínio de valores | Descrição |
|---|---|---|---|
| sk_vendedor | BIGINT | sequencial, não nulo, único | Chave substituta |
| seller_id | STRING | 32 caracteres hexadecimais | Chave de negócio do vendedor |
| seller_city | STRING | nomes de cidade em minúsculo | Cidade do vendedor |
| seller_state | STRING | 27 UFs do Brasil | Estado do vendedor |

**Linhagem:** `olist_sellers_dataset.csv` → Bronze → Silver: padronização de texto → Gold: `gold.dim_vendedor`.

### 2.4 dim_data

| Coluna | Tipo | Domínio de valores | Descrição |
|---|---|---|---|
| data | DATE | intervalo coberto pelo dataset (~2016-09 a 2018-10) | Chave (a própria data) |
| ano | INT | 2016–2018 | Ano |
| mes | INT | 1–12 | Mês |
| dia | INT | 1–31 | Dia do mês |
| nome_mes | STRING | Janeiro–Dezembro | Nome do mês por extenso |
| trimestre | INT | 1–4 | Trimestre |
| dia_da_semana | STRING | Domingo–Sábado | Dia da semana |
| fim_de_semana | BOOLEAN | true/false | Indica sábado ou domingo |

**Linhagem:** gerada programaticamente (não vem de CSV de origem) via `sequence()` de datas cobrindo do mínimo ao máximo entre `order_purchase_timestamp`, `order_delivered_customer_date` e `order_estimated_delivery_date` em todas as tabelas de origem → Gold: `gold.dim_data`.

### 2.5 dim_pedido

| Coluna | Tipo | Domínio de valores | Descrição |
|---|---|---|---|
| sk_pedido | BIGINT | sequencial, não nulo, único | Chave substituta |
| order_id | STRING | 32 caracteres hexadecimais | Chave de negócio do pedido |
| sk_cliente | BIGINT | FK → dim_cliente | Cliente que fez o pedido |
| order_status | STRING | delivered, shipped, canceled, etc. (8 valores) | Status do pedido |
| data_compra | DATE | FK → dim_data | Data da compra |
| dias_atraso | INT | pode ser negativo (entregue antes do prazo) ou nulo (não entregue) | `order_delivered_customer_date - order_estimated_delivery_date`, em dias |

**Linhagem:** `olist_orders_dataset.csv` → Bronze → Silver: parse de timestamps, cálculo de `dias_atraso`, join com `olist_customers_dataset` para resolver `customer_id → customer_unique_id` → Gold: `gold.dim_pedido` (adiciona `sk_pedido`, `sk_cliente` via lookup em `dim_cliente`).

**Nota de qualidade:** pedidos com `order_status != 'delivered'` têm `order_delivered_customer_date` nulo, portanto `dias_atraso` nulo — tratado como "não aplicável", não como zero.

---

## 3. Fatos

### 3.1 fato_pedido_itens

Grão: 1 linha por item de pedido (um pedido com 3 itens gera 3 linhas).

| Coluna | Tipo | Domínio | Descrição |
|---|---|---|---|
| sk_pedido | BIGINT | FK → dim_pedido | Pedido |
| sk_produto | BIGINT | FK → dim_produto | Produto |
| sk_vendedor | BIGINT | FK → dim_vendedor | Vendedor |
| order_item_id | INT | ≥ 1 | Número sequencial do item dentro do pedido |
| price | DECIMAL(10,2) | ≥ 0 | Preço do item |
| freight_value | DECIMAL(10,2) | ≥ 0 | Valor do frete do item |

**Linhagem:** `olist_order_items_dataset.csv` → Bronze → Silver: tipagem de `price`/`freight_value` → Gold: join com as três dimensões para resolver surrogate keys.

**Perguntas de negócio servidas:** 1 (entrega x satisfação, via join com dim_pedido), 2 (receita por categoria), 3a/3b (logística/CD por estado, via dim_vendedor/dim_cliente).

### 3.2 fato_pagamentos

Grão: 1 linha por forma de pagamento usada em um pedido (pedidos pagos em 2 cartões geram 2 linhas).

| Coluna | Tipo | Domínio | Descrição |
|---|---|---|---|
| sk_pedido | BIGINT | FK → dim_pedido | Pedido |
| payment_sequential | INT | ≥ 1 | Ordem da forma de pagamento no pedido |
| payment_type | STRING | credit_card, boleto, voucher, debit_card, not_defined | Forma de pagamento |
| payment_installments | INT | ≥ 0 | Número de parcelas |
| payment_value | DECIMAL(10,2) | ≥ 0 | Valor pago nessa forma |

**Linhagem:** `olist_order_payments_dataset.csv` → Bronze → Silver: tipagem → Gold: join com dim_pedido.

**Perguntas de negócio servidas:** 4 (forma de pagamento x parcelas x valor).

### 3.3 fato_avaliacoes

Grão: 1 linha por avaliação de pedido.

| Coluna | Tipo | Domínio | Descrição |
|---|---|---|---|
| sk_pedido | BIGINT | FK → dim_pedido | Pedido avaliado |
| review_score | INT | 1–5 | Nota da avaliação |
| dias_resposta | INT | ≥ 0 | `review_answer_timestamp - review_creation_date`, em dias |

**Linhagem:** `olist_order_reviews_dataset.csv` → Bronze → Silver: tipagem de datas, cálculo de `dias_resposta`, deduplicação de reviews duplicadas por `review_id` → Gold: join com dim_pedido.

**Perguntas de negócio servidas:** 1 (entrega x satisfação), 6 (performance de vendedor x avaliação, via join fato_avaliacoes → dim_pedido → fato_pedido_itens → dim_vendedor).

---

## 4. Perguntas de negócio → tabelas necessárias (rastreabilidade)

| # | Pergunta | Fatos/Dimensões usadas |
|---|---|---|
| 1 | Atraso x satisfação | fato_avaliacoes + dim_pedido (dias_atraso) |
| 2 | Receita por categoria | fato_pedido_itens + dim_produto |
| 3a | Estado para novo CD | fato_pedido_itens + dim_pedido + dim_cliente + dim_vendedor |
| 3b | Categorias por estado | fato_pedido_itens + dim_produto + dim_cliente |
| 4 | Pagamento x parcelas | fato_pagamentos |
| 5 | Sazonalidade mensal | fato_pedido_itens + dim_data |
| 6 | Vendedor x avaliação | fato_avaliacoes + dim_pedido + fato_pedido_itens + dim_vendedor |
| 7 | Recência/recompra | dim_pedido + dim_cliente (customer_unique_id) |

---

## 5. Dimensões de qualidade de dados aplicadas (Silver)

Conforme material da disciplina (Completude, Consistência, Unicidade, Acurácia, Outliers):

- **Completude:** verificação de nulos em colunas-chave (`order_id`, `customer_id`, `product_id`); tratamento explícito de nulos em `product_category_name` e datas de entrega não concluída.
- **Consistência:** padronização de tipos (datas como TIMESTAMP/DATE, valores monetários como DECIMAL), padronização de texto (lower/trim em cidade/estado).
- **Unicidade:** deduplicação por chave de negócio em todas as dimensões (`dropDuplicates`), verificação de `review_id` duplicado em avaliações.
- **Acurácia:** validação de domínio (`review_score` entre 1–5, `payment_installments` ≥ 0, estados dentro das 27 UFs válidas).
- **Outliers:** identificação de valores de `price`/`freight_value` extremos (ex. > 3 desvios-padrão da média) para decisão de manter ou sinalizar na análise final.

Essas verificações serão detalhadas com evidências (prints/contagens) no notebook e documento de Qualidade de Dados (Etapa 4.4, próxima etapa após o ETL).
