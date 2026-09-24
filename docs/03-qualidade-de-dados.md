# Qualidade de Dados (Etapa 4.4)

Este documento registra as verificações de qualidade aplicadas na camada Silver (`notebooks/02_silver_limpeza.py`), organizadas pelas cinco dimensões de qualidade de dados trabalhadas na disciplina: **Completude, Consistência, Unicidade, Acurácia e Outliers**.

## 1. Completude — `customers`

**Verificação:** contagem de linhas com `customer_unique_id` nulo após a limpeza (essa coluna é a chave de negócio usada em `dim_cliente` e não pode ter nulos).

**Resultado:**
```
customers: 0 linhas com customer_unique_id nulo (esperado: 0)
```

**Conclusão:** completude 100% garantida na chave de cliente. Nenhuma ação corretiva necessária.

## 2. Acurácia — `orders`

**Verificação:** contagem de pedidos cujo `order_status` está fora do domínio de valores esperado (`delivered`, `shipped`, `canceled`, `unavailable`, `invoiced`, `processing`, `created`, `approved`).

**Resultado:**
```
orders: 0 linhas com order_status fora do domínio esperado
```

**Conclusão:** todos os valores de status observados no dataset pertencem ao domínio esperado — não há valores inválidos ou digitados incorretamente.

## 3. Completude — `products` (categoria)

**Verificação:** percentual de produtos sem `product_category_name` original (nulo na fonte).

**Resultado:**
```
products: 1.89% dos produtos sem categoria original
```

**Decisão de tratamento:** em vez de descartar essas linhas (o que reduziria a receita contabilizada nas análises da pergunta de negócio 2), elas foram mantidas e marcadas explicitamente como `categoria_nao_informada` na camada Silver/Gold. Isso preserva o volume de dados e torna o problema visível nas agregações, em vez de escondê-lo com uma exclusão silenciosa.

## 4. Outliers — `order_items` (preço)

**Verificação:** contagem de itens de pedido com `price` acima de média + 3 desvios-padrão.

**Resultado:**
```
order_items: 1966 itens com price acima de média+3dp (limite=671.56)
```

**Análise:** 1.966 itens (≈1,75% dos 112.650 itens totais) têm preço acima de R$ 671,56. Dado que o Olist é um marketplace com produtos de categorias muito diferentes (de acessórios a móveis e eletrônicos), preços altos não são necessariamente erros de digitação — podem refletir produtos legítimos de categorias de ticket alto (ex.: eletrônicos, móveis).

**Decisão de tratamento:** os outliers **não foram removidos** da base. Eles foram apenas identificados e quantificados nesta etapa; a decisão de excluir, capar (winsorizing) ou manter será avaliada pontualmente na Etapa de Análise (notebook 04), caso algum desses valores distorça significativamente uma métrica específica (ex.: ticket médio por categoria).

## 5. Unicidade — aplicada em todas as dimensões

Verificação por deduplicação (`dropDuplicates`) pela chave de negócio de cada entidade:
- `customers`: dedup por `customer_id` (Silver) e por `customer_unique_id` (Gold, na construção de `dim_cliente`).
- `orders`: dedup por `order_id`.
- `products`: dedup por `product_id`.
- `sellers`: dedup por `seller_id`.
- `order_reviews`: dedup por `review_id` (reviews duplicadas identificadas e removidas).

Nenhuma duplicata residual foi encontrada após a deduplicação — confirmado indiretamente pela contagem de linhas da camada Gold bater exatamente com a contagem esperada de chaves únicas (ex.: `dim_vendedor` = 3.095 linhas = número de `seller_id` únicos na fonte).

## 6. Consistência — tipos e formatos

Aplicada em todas as tabelas Silver:
- Datas convertidas de `STRING` para `TIMESTAMP`/`DATE` (`orders`, `order_items`, `order_reviews`).
- Valores monetários convertidos para `DECIMAL(10,2)` (`order_items.price`, `order_items.freight_value`, `order_payments.payment_value`).
- Texto padronizado em minúsculo/maiúsculo consistente (`customer_city`/`seller_city` em minúsculo; `customer_state`/`seller_state` em maiúsculo).
- Correção de parsing de CSV multilinha: o campo `review_comment_message` contém quebras de linha e vírgulas dentro de texto entre aspas, o que inicialmente causava desalinhamento de colunas na leitura (erro `CAST_INVALID_INPUT` — um trecho de comentário de cliente foi parar na coluna `review_creation_date`). Corrigido na leitura Bronze com as opções `multiLine`, `quote` e `escape` do leitor CSV do Spark.

## 7. Resumo consolidado

| Dimensão de qualidade | Tabela | Achado | Ação tomada |
|---|---|---|---|
| Completude | customers | 0% nulos em customer_unique_id | Nenhuma |
| Acurácia | orders | 0 status fora do domínio | Nenhuma |
| Completude | products | 1,89% sem categoria | Marcado como "categoria_nao_informada" |
| Outliers | order_items | 1.966 itens (1,75%) com preço > média+3dp | Mantidos, sinalizados para revisão na Análise |
| Unicidade | todas as dimensões | duplicatas removidas por chave de negócio | dropDuplicates aplicado |
| Consistência | orders, order_items, order_reviews | tipos e parsing de CSV corrigidos | Cast de tipos + opções multiLine/quote/escape |
