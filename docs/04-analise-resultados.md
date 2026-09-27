# Análise: Respostas às Perguntas de Negócio (Etapa 5)

> Resultados obtidos a partir das tabelas Gold (`notebooks/04_analise_perguntas_negocio.py`), executado no Databricks sobre o dataset Olist.

---

## 1. Entrega x satisfação
**O atraso na entrega (data real vs. estimada) impacta a nota de avaliação (`review_score`)?**

| Faixa de atraso | Nota média | Nº avaliações |
|---|---|---|
| No prazo ou antecipado | 4.29 | 89.245 |
| Atraso leve (1–3 dias) | 3.29 | 1.843 |
| Atraso grande (4+ dias) | 1.85 | 4.519 |
| Sem informação de entrega | 1.74 | 2.803 |

Há uma influência clara e direta do prazo de entrega na nota média de avaliação. Os números mostram uma boa eficiência logística no geral: cerca de 90% das entregas ocorrem no prazo ou de forma antecipada.

Dois achados se destacam:

1. **Atraso leve já derruba a nota para um patamar neutro** (3.29), o que indica uma janela de oportunidade: ações pontuais e de baixo custo — como frete grátis na próxima compra ou cupons de desconto — têm boa chance de reverter a percepção do cliente nesse estágio inicial. Já na faixa de atraso grande, a nota despenca para 1.85, sinal de que o cliente já entra em um cenário de forte insatisfação (detração), onde a reversão exige muito mais energia e recurso — atendimento individualizado, campanhas agressivas de desconto/benefícios — e, mesmo assim, o cenário muitas vezes não é revertido.

2. **A faixa de atraso grande tem quase 4x mais avaliações que a de atraso leve.** Isso mostra que atacar as causas dos atrasos mais graves (não os leves) traria o maior impacto agregado nas avaliações da empresa, reduzindo custos com campanhas de recuperação e abrindo mais espaço para recompra (aumento de LTV da base).

---

## 2. Receita por categoria
**Quais categorias de produto têm maior ticket médio e maior participação na receita total?**

| Categoria | Ticket médio | Receita total | % receita | Nº itens |
|---|---|---|---|---|
| health_beauty | 130.16 | 1.258.681,34 | 9,26% | 9.670 |
| watches_gifts | 201.14 | 1.205.005,68 | 8,87% | 5.991 |
| bed_bath_table | 93.30 | 1.036.988,68 | 7,63% | 11.115 |
| sports_leisure | 114.34 | 988.048,97 | 7,27% | 8.641 |
| computers_accessories | 116.51 | 911.954,32 | 6,71% | 7.827 |
| furniture_decor | 87.56 | 729.762,49 | 5,37% | 8.334 |
| cool_stuff | 167.36 | 635.290,85 | 4,67% | 3.796 |
| housewares | 90.79 | 632.248,66 | 4,65% | 6.964 |
| auto | 139.96 | 592.720,11 | 4,36% | 4.235 |
| garden_tools | 111.63 | 485.256,46 | 3,57% | 4.347 |

`health_beauty` lidera a participação na receita total, seguida de `watches_gifts` e `bed_bath_table`. Vale notar categorias com ticket médio elevado mas participação menor na receita — `cool_stuff`, `auto`, `baby`, `office_furniture` — que vendem menos unidades, porém a um preço mais alto por item.

Esta análise não aprofunda a margem de lucro de cada categoria (dado não disponível no dataset); fica como recomendação para um direcionamento estratégico mais preciso de campanhas de mídia paga nessas categorias de ticket alto.

---

## 3a. Logística — novo Centro de Distribuição
**Qual estado seria mais indicado para receber um novo CD/hub?**

| Estado | Nº pedidos | Frete médio | Atraso médio (dias) |
|---|---|---|---|
| SP | 41.376 | 15,15 | -11,21 |
| RJ | 12.761 | 20,96 | -12,01 |
| MG | 11.543 | 20,63 | -13,34 |
| RS | 5.432 | 21,74 | -14,13 |
| PR | 4.998 | 20,52 | -13,49 |
| SC | 3.614 | 21,48 | -11,57 |
| BA | 3.358 | 26,36 | -10,98 |
| DF | 2.124 | 21,04 | -12,20 |
| ES | 2.024 | 22,06 | -10,64 |
| GO | 2.010 | 22,76 | -12,30 |

**Estado escolhido: Minas Gerais (MG)**

Justificativa: MG é o 3º estado em volume de pedidos e já figura entre os 3 piores em atraso médio de entrega, mesmo sem ter o frete mais caro do país (não está no top 5). Cruzando volume de pedidos com atraso médio, MG desponta como o candidato mais forte para reduzir detratores dentro do próprio estado.

Outro argumento a favor de MG é sua posição geográfica: proximidade com estados de custo de frete mais elevado, como os do Centro-Oeste (GO, DF), que poderiam ser atendidos por um hub mineiro. A região Sul também sofre com fretes altos, mas Minas Gerais tem vantagem por contar com uma malha logística rodoviária mais ampla e central no país.

---

## 3b. Logística — categorias no estado escolhido (MG)
**Quais categorias de produto teriam maior demanda/volume nesse estado?**

| Categoria | Nº itens | Receita total |
|---|---|---|
| bed_bath_table | 1.331 | 129.643,98 |
| health_beauty | 1.085 | 157.491,31 |
| computers_accessories | 1.000 | 111.069,74 |
| sports_leisure | 965 | 112.534,19 |
| furniture_decor | 950 | 79.064,64 |
| housewares | 835 | 78.073,72 |
| watches_gifts | 637 | 123.759,23 |
| garden_tools | 608 | 60.649,22 |
| auto | 514 | 72.897,98 |
| toys | 493 | 58.816,40 |

O perfil de demanda em MG reproduz de perto o ranking nacional da pergunta 2 (`bed_bath_table`, `health_beauty`, `computers_accessories` e `sports_leisure` aparecem no topo em ambos). Isso reforça a decisão da pergunta 3a: um hub em MG não estaria apostando em categorias atípicas, mas justamente nas de maior giro e receita já validadas em escala nacional — o que reduz o risco de estoque parado e justifica priorizar essas categorias no CD.

Vale notar que `health_beauty` e `watches_gifts`, apesar de menor volume de itens que `bed_bath_table`, geram receita comparável ou maior — reflexo do ticket médio mais alto dessas categorias (visto na pergunta 2) — o que as torna boas candidatas a estoque priorizado por valor agregado, não só por volume.

---

## 4. Forma de pagamento
**Qual a forma de pagamento mais usada e como o número de parcelas se relaciona ao valor do pedido?**

| Forma de pagamento | Nº pagamentos | Parcelas médias | Valor médio |
|---|---|---|---|
| credit_card | 76.795 | 3,51 | 163,32 |
| boleto | 19.784 | 1,00 | 145,03 |
| voucher | 5.775 | 1,00 | 65,70 |
| debit_card | 1.529 | 1,00 | 142,57 |
| not_defined | 3 | 1,00 | 0,00 |

O cartão de crédito é disparado a forma de pagamento mais usada (73,3% dos pagamentos) e a única que permite parcelamento no dataset — as demais formas (boleto, voucher, débito) registram sempre 1 parcela. Além disso, o cartão de crédito tem o maior valor médio de pedido (R$ 163,32), sugerindo que o parcelamento é um fator facilitador para compras de ticket mais alto: o cliente consegue comprar mais caro porque pode dividir o pagamento.

**Ressalva:** este dataset é de 2016–2018, período anterior à adoção em massa do PIX no Brasil (lançado em 2020). É provável que esse cenário de concentração em cartão de crédito tenha mudado significativamente hoje, com o PIX capturando parte relevante das transações à vista que antes iam para boleto ou débito.

---

## 5. Sazonalidade mensal

Existe uma tendência de **crescimento consistente** no volume de pedidos e receita ao longo de 2017, que se estabiliza em um patamar mais alto durante 2018. O destaque isolado é **novembro de 2017** (7.451 pedidos, R$ 1.010.271,37 em receita) — um salto muito acima da tendência dos meses vizinhos, coincidindo com o período de Black Friday, o que indica forte sazonalidade associada a essa data comercial.

**Ressalva importante:** os meses nas extremidades do dataset (setembro a dezembro de 2016, e setembro de 2018) têm volumes quase nulos (1 a 308 pedidos, contra milhares nos meses "cheios"). Isso não é sazonalidade real — é um artefato de cobertura incompleta do dataset nessas bordas (o Olist provavelmente só começou a operar/ter volume relevante em 2017, e a extração dos dados foi interrompida no meio de setembro/2018). Esses meses de borda foram desconsiderados na leitura de tendência acima.

---

## 6. Performance de vendedor x avaliação
**Vendedores com tempo médio de entrega menor recebem avaliações melhores?**

A consulta retornou os ~600 vendedores com 10+ pedidos, ordenados por nota média. Resumo dos extremos:

| Grupo | Atraso médio típico | Nota média |
|---|---|---|
| Top 10 vendedores (melhor nota, ~4.8–5.0) | entre -24 e -8 dias (entrega bem adiantada) | 4,82 a 5,00 |
| 10 piores vendedores (pior nota, ~1.3–3.3) | entre -48 e +4 dias (mais variável, alguns com atraso real) | 1,26 a 3,30 |

**Achado principal:** existe uma relação entre entrega adiantada e nota alta — os vendedores mais bem avaliados entregam consistentemente bem antes do prazo estimado. Porém, essa relação é **mais fraca e mais ruidosa** entre os vendedores pior avaliados: vários deles também entregam adiantado (alguns até com grande antecedência, como -48 dias) e ainda assim têm nota baixa, o que indica que **o tempo de entrega não é o único fator** por trás de uma nota ruim — qualidade do produto, comunicação e atendimento do vendedor provavelmente pesam tanto quanto ou mais que a logística nesses casos.

Isso é consistente com a pergunta 1: o atraso de entrega tem impacto claro e forte na nota quando olhamos por pedido individual, mas ao agregar por vendedor, outros fatores do próprio vendedor diluem esse sinal.

*(A tabela completa com os ~600 vendedores está disponível na saída do notebook `04_analise_perguntas_negocio.py` no Databricks, usada como evidência/screenshot, mas não reproduzida por extenso aqui por tamanho.)*

---

## 7. Recência e recompra

| Total de clientes | Clientes com recompra | Taxa de recompra |
|---|---|---|
| 96.096 | 2.997 | 3,12% |

| Dias médios entre 1ª e 2ª compra |
|---|
| 80,3 |

**Achado principal:** a taxa de recompra é muito baixa — apenas 3,12% dos clientes únicos (`customer_unique_id`) fizeram uma segunda compra no período coberto pelo dataset. Entre os que recompram, o intervalo médio entre a 1ª e a 2ª compra é de 80,3 dias (pouco menos de 3 meses).

Esse número é baixo mesmo para um marketplace (onde a recorrência tende a ser naturalmente menor que em e-commerces de nicho ou assinatura), e representa a maior oportunidade de negócio identificada nesta análise: **a aquisição de clientes está funcionando, mas a retenção não.** Isso sugere investimento em CRM/e-mail marketing pós-compra, cupons de segunda compra com prazo alinhado à janela de ~80 dias observada, e programas de fidelidade — ações que teriam potencial de aumentar o LTV da base sem depender de novos investimentos em aquisição.

**Ressalva:** a taxa real de recompra pode estar sublimada porque parte da base de clientes de "primeira compra" fez essa compra perto do fim do período coberto pelo dataset (2018), sem tempo suficiente para uma eventual segunda compra aparecer nos dados — um efeito de censura à direita comum em análises de janela fixa.

---

## Observações gerais / dificuldades encontradas

- O maior desafio técnico foi de qualidade/parsing dos dados brutos, não de modelagem: o campo `review_comment_message` continha quebras de linha e vírgulas dentro de texto entre aspas, o que inicialmente corrompia o parsing do CSV e deslocava colunas inteiras (detalhado em `docs/03-qualidade-de-dados.md`).
- A pergunta 6 evidenciou uma limitação de generalização: relações fortes observadas no nível de pedido individual (pergunta 1) não necessariamente se mantêm com a mesma força quando agregadas por vendedor — um lembrete de que a granularidade da análise muda a conclusão.
- Com mais tempo, seria valioso: (1) trazer dados de margem por categoria para complementar a pergunta 2; (2) rodar um teste estatístico formal (não só comparação de médias) para validar a significância do achado da pergunta 1; (3) investigar mais a fundo os vendedores da pergunta 6 que entregam adiantado mas têm nota baixa, cruzando com `review_comment_message` para entender a causa real da insatisfação.
