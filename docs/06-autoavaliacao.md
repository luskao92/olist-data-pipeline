# Autoavaliação

> Rascunho — revisar e ajustar para refletir sua visão pessoal antes de finalizar.

## Objetivos atingidos

O objetivo inicial era construir um pipeline de dados completo (Bronze → Silver → Gold) sobre o dataset Olist e responder 7 perguntas de negócio ligadas a satisfação do cliente, receita, logística, pagamento, sazonalidade e recompra. Esse objetivo foi atingido: as 7 perguntas foram respondidas com dados reais extraídos do modelo dimensional construído, com discussão e recomendações de negócio para cada uma.

O modelo de dados evoluiu de uma ideia inicial de esquema estrela simples para uma **constelação de fatos** (3 fatos, 5 dimensões), decisão tomada ao perceber que as perguntas de negócio operavam em grãos diferentes (item de pedido, pagamento, avaliação) que não caberiam bem em uma única tabela fato.

## Dificuldades encontradas

- **Restrição de tempo real**: a disponibilidade de produção foi bem menor do que o cronograma inicial previa (rotina de trabalho em horário comercial + poucas noites livres), o que exigiu recalibrar o escopo e a ordem de prioridade das etapas ao longo da semana.
- **Qualidade de dados do CSV bruto**: o campo de comentário de avaliação (`review_comment_message`) contém texto livre com vírgulas e quebras de linha dentro de aspas, o que inicialmente corrompia o parsing do CSV e deslocava colunas inteiras — um problema sutil, só percebido ao investigar um erro de tipo aparentemente não relacionado.
- **Ambiente Databricks Free Edition**: por bloquear automação de navegador (medida de segurança da própria plataforma), grande parte da configuração inicial (criação de Volume, upload de arquivos, sincronização via Repos) precisou ser feita manualmente, passo a passo.
- **Erros de schema em reexecuções**: o Delta Lake exige autorização explícita (`overwriteSchema=true`) para mudar o schema de uma tabela já existente, o que gerou alguns erros até esse comportamento ficar claro.

## Trabalhos futuros

- Trazer dados de margem/custo por categoria de produto, para complementar a análise de receita (pergunta 2) com uma visão de rentabilidade, não só de faturamento.
- Aplicar testes estatísticos formais (não só comparação de médias) para validar a significância dos achados, principalmente da pergunta 1 (atraso x satisfação).
- Investigar mais a fundo os vendedores com entrega adiantada mas nota baixa (achado da pergunta 6), cruzando com o texto das avaliações para entender a causa raiz da insatisfação.
- Explorar o dataset de dados abertos do TSE (candidaturas/eleições) como um segundo projeto de portfólio, ideia que foi cogitada e descartada neste MVP por restrição de tempo.
- Automatizar o pipeline com um agendamento (Databricks Jobs), transformando-o de uma execução manual para uma rotina de atualização periódica.
