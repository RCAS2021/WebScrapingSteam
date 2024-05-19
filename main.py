from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import csv
import re
from datetime import datetime

# Inicia o driver do navegador (neste caso, Chrome)
driver = webdriver.Chrome()

# Abre a página
driver.get('https://store.steampowered.com/search/?sort_by=Reviews_DESC&specials=1&ndl=1')

# Aguarda até que o conteúdo da página seja carregado
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'search_result_row')))

# Continua rolando até o final da página ou até que não haja mais novos jogos sendo carregados
last_height = driver.execute_script("return document.body.scrollHeight")

# Inicializa o arquivo CSV e escreve o cabeçalho
with open('steam_deals3.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(["Titulo", "Data de Lancamento", "Preco Original", "Preco Final", "Analise de Sentimento", "Porcentagem de Reviews Positivas", "Total de Reviews", "Porcentagem de Desconto", "Data da Consulta"])

processed_titles = set()  # Conjunto para rastrear os títulos dos jogos já processados

while True:
    # Inicializando lista vazia no início de cada iteração
    games = []

    # Agora que a página está totalmente carregada, podemos analisá-la com o BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'lxml')

    # Capturando dados
    data_body = soup.find_all('div', {'class': 'col search_name ellipsis'})
    data_released = soup.find_all('div', {'class': 'col search_released responsive_secondrow'})
    data_prices = soup.find_all('div', {'class': 'discount_prices'})
    data_reviews = soup.find_all('span', {'class': 'search_review_summary'})
    data_discount_pct = soup.find_all('div', {'class': 'discount_pct'})

    print(f"Encontrados {len(data_body)} jogos na página atual.")

    for i in range(len(data_body)):
        game_title = data_body[i].text.strip().replace('\n', '').replace('\r', '') if i < len(data_body) else None
        
        # Ignora jogos já processados
        if game_title in processed_titles:
            continue

        release_date = data_released[i].text.strip().replace('\n', '').replace('\r', '') if i < len(data_released) else None
        
        if i < len(data_prices):
            prices = data_prices[i].text.strip().split('R$', 2)
            original_price = 'R$' + prices[1].strip().replace('\n', '').replace('\r', '') if len(prices) > 1 else None
            final_price = 'R$' + prices[-1].strip().replace('\n', '').replace('\r', '') if prices else None
            # Remove 'Preço p/ você:' do preço original, se estiver presente
            if original_price and 'Preço p/ você:' in original_price:
                original_price = original_price.replace('Preço p/ você:', '').strip()
        else:
            original_price = None
            final_price = None

        discount_pct = data_discount_pct[i].text.strip() if i < len(data_discount_pct) and data_discount_pct[i].text.strip() else None
        # Converte a porcentagem de desconto para um número inteiro
        discount = int(discount_pct.replace('%', '')) if discount_pct else 0

        if i < len(data_reviews) and data_reviews[i].has_attr('data-tooltip-html'):
            tooltip_html = data_reviews[i]['data-tooltip-html']
            match = re.search(r'(\d+)% das? (\d{1,3}(?:\,\d{3})*) análises', tooltip_html)
            if match:
                positive_review_pct = int(match.group(1))
                total_reviews = int(match.group(2).replace(',', ''))
            else:
                positive_review_pct = 0
                total_reviews = 0

            review_sentiment = tooltip_html.split('<br>')[0]
            
            # Debug print para verificar se os valores foram capturados corretamente
            print(f"Game: {game_title}, Reviews: {total_reviews}, Positive %: {positive_review_pct}")
        else:
            review_sentiment = None
            positive_review_pct = 0
            total_reviews = 0

        # Verifica se o jogo atende aos critérios de filtro
        if discount <= -50 and positive_review_pct >= 60 and total_reviews > 500:
            game = [
                game_title,
                release_date,
                original_price,
                final_price,
                review_sentiment,
                positive_review_pct,
                total_reviews,
                discount_pct,
                datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            ]
            games.append(game)
            processed_titles.add(game_title)  # Adiciona o título do jogo ao conjunto de processados

    # Salva os dados em um arquivo CSV
    if games:
        with open('steam_deals3.csv', 'a', newline='', encoding='utf-8') as f:  # Note que estamos usando 'a' para anexar em vez de 'w' para escrever
            writer = csv.writer(f)
            writer.writerows(games)  # Faz uma cópia da lista games
            print(f"{len(games)} ofertas salvas em steam_deals3.csv")

    # Rola a página
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)  # aguarda o carregamento da página
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# Não se esqueça de fechar o driver quando terminar
driver.quit()