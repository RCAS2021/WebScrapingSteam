# beAnalytic
Case técnico realizado para vaga de Engenharia de Dados Jr na empresa beAnalytic.

Tarefas:

1- Realizar a extração das informações da base de dados do steamdb.info/sales:

Como o steamdb não permite web scraping e nem disponibiliza uma API para acessar seus dados,
realizei o web scraping da loja da steam diretamente, através do site:
https://store.steampowered.com/search/?specials=1&ndl=1
---|

Os dados coletados foram:
- Título do jogo
- Data de lançamento
- Preço original
- Preço final
- Análises
- Porcentagem de desconto
- Data da consulta

2- Armazenar esses dados no Google BigQuery:

Para realizar essa tarefa, salvei os dados gerados pelo web scraping em um arquivo csv e criei o conjunto de dados e a tabela no Google Cloud Console.

3- Conectar os dados em uma planilha do Google Sheets:

Para realizar essa tarefa, criei uma planilha no Google Sheets e adicionei os dados através do menu Dados -> Conetores de dados -> Associar ao BigQuery

Link da planilha do Google Sheets:
https://docs.google.com/spreadsheets/d/1uJQ_YPjpSLznm2S0guw-YyRsagap_rEAbUYeO-qqEj8/edit?usp=sharing