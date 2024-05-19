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
while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)  # aguarda o carregamento da página
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# Agora que a página está totalmente carregada, podemos analisá-la com o BeautifulSoup
soup = BeautifulSoup(driver.page_source, 'lxml')

# Capturando dados
data_body = soup.find_all('div', {'class':'col search_name ellipsis'})
data_released = soup.find_all('div', {'class':'col search_released responsive_secondrow'})
data_prices = soup.find_all('div', {'class':'discount_prices'})
data_reviews = soup.find_all('span', {'class':'search_review_summary'})
data_discount_pct = soup.find_all('div', {'class':'discount_pct'})

# Inicializando lista vazia
games = []

for i in range(len(data_body)):
    prices = data_prices[i].text.strip().split('R$', 2) if i < len(data_prices) else None
    original_price = 'R$' + prices[1].strip().replace('\n', '').replace('\r', '') if prices else None
    final_price = 'R$' + prices[-1].strip().replace('\n', '').replace('\r', '') if prices else None

    # Remove 'Preço p/ você:' do preço original, se estiver presente
    if original_price and 'Preço p/ você:' in original_price:
        original_price = original_price.replace('Preço p/ você:', '').strip()

    release_date = data_released[i].text.strip().replace('\n', '').replace('\r', '') if i < len(data_released) else None

    review = data_reviews[i]['data-tooltip-html'].split('<br>')[0] if i < len(data_reviews) and data_reviews[i]['data-tooltip-html'] else None

    discount_pct = data_discount_pct[i].text.strip() if i < len(data_discount_pct) and data_discount_pct[i].text.strip() else None

    game_title = data_body[i].text.strip().replace('\n', '').replace('\r', '') if i < len(data_body) else None


    if i < len(data_reviews) and data_reviews[i].has_attr('data-tooltip-html'):
        tooltip_html = data_reviews[i]['data-tooltip-html']
        match = re.search(r'(\d+)% das? (\d{1,3}(?:\,\d{3})*) análises', tooltip_html)
        if match:
            positive_review_pct = int(match.group(1))
            total_reviews = int(match.group(2).replace(',', ''))
        else:
            positive_review_pct = 0
            total_reviews = 0

        review = tooltip_html.split('<br>')[0]
    
    discount_pct = data_discount_pct[i].text.strip() if i < len(data_discount_pct) and data_discount_pct[i].text.strip() else None
    # Converte a porcentagem de desconto para um número inteiro
    discount = int(discount_pct.replace('%', '')) if discount_pct else 0

    if discount <= -50 and total_reviews > 500 and positive_review_pct >= 60:
        positive_review_pct = f'{positive_review_pct}%' 

        game = [
            game_title,
            release_date,
            original_price,
            final_price,
            positive_review_pct,
            discount_pct,
            total_reviews,
            datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        ]
        games.append(game)
    elif positive_review_pct < 60:
        print('Porcentagem de análises positivas menor do que 60. terminando.')
        break

# Salva os dados em um arquivo CSV
with open('steam_deals.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(["Titulo", "Data de Lancamento", "Preco Original", "Preco Final", "Porcentagem Analises Positivas", "Porcentagem de Desconto", "Total de Reviews", "Data da Consulta"])  # Escreve o cabeçalho
    writer.writerows(games)  # Escreve os dados

print(f"{len(games)} ofertas salvas em steam_deals.csv")

# Não se esqueça de fechar o driver quando terminar
driver.quit()