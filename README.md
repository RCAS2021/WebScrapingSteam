# Web Scraping Steam
Tarefas:

1- Realizar a extração das informações de jogos em promoção na steam, com os filtros rating >= 60, reviews >= 500 e discount >= 50%:
https://store.steampowered.com/search/?sort_by=Reviews_DESC&specials=1&ndl=1
---|

Os dados coletados foram:
- Título do jogo
- Data de lançamento
- Preço original
- Preço final
- Porcentagem de análises positivas
- Porcentagem de desconto
- Total de reviews
- Data da consulta

2- Armazenar esses dados no Google BigQuery:

Para realizar essa tarefa, salvei os dados gerados pelo web scraping em um arquivo csv e criei o conjunto de dados e a tabela no Google Cloud Console.

3- Conectar os dados em uma planilha do Google Sheets:

Para realizar essa tarefa, criei uma planilha no Google Sheets e adicionei os dados através do menu Dados -> Conetores de dados -> Associar ao BigQuery
