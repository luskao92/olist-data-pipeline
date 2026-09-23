# Contexto de Negócios e Perguntas (Etapa 2 e 4.1)

## Problema

Quero entender quais fatores impactam a satisfação do cliente e a performance comercial e logística no e-commerce da Olist, para identificar oportunidades de melhoria operacional e comercial.

## Perguntas de negócio

1. **Entrega x satisfação**: o atraso na entrega (data real vs. estimada) impacta a nota de avaliação (`review_score`)?
2. **Receita por categoria**: quais categorias de produto têm maior ticket médio e maior participação na receita total?
3. **Logística e expansão**:
   - 3a. Qual estado seria mais indicado para receber um novo Centro de Distribuição (CD)/hub, considerando volume de pedidos, custo médio de frete e tempo de entrega (real vs. estimado) para aquela região?
   - 3b. Quais categorias de produto teriam maior demanda/volume nesse estado, justificando estoque prioritário nesse hub?
4. **Pagamento**: qual a forma de pagamento mais usada e como o número de parcelas se relaciona ao valor do pedido?
5. **Sazonalidade**: existe sazonalidade mensal nas vendas ao longo do período coberto pelo dataset?
6. **Performance de vendedor**: vendedores com tempo médio de entrega menor recebem avaliações melhores?
7. **Recência e recompra**: qual a taxa de clientes que fazem mais de uma compra (usando `customer_unique_id`, não `customer_id`) e qual o tempo médio entre a primeira e a segunda compra, entre os que recompram?

## Fonte de dados

**Dataset**: Olist Brazilian E-commerce Public Dataset (Kaggle) — https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
**Licença**: CC BY-NC-SA 4.0 (uso não comercial, com atribuição, compartilhamento pela mesma licença) — compatível com o uso acadêmico deste MVP.

## Nota de qualidade de dados já identificada

O campo `customer_id` do dataset é praticamente único por pedido — não identifica a mesma pessoa em compras diferentes. A identificação real do cliente ao longo do tempo deve usar `customer_unique_id`. Isso será tratado na etapa de Qualidade de Dados e é essencial para a Pergunta 7.
