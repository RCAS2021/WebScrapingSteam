from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import csv
from datetime import datetime

# Inicia o driver do navegador (neste caso, Chrome)
driver = webdriver.Chrome()

# Abre a página
driver.get('https://store.steampowered.com/search/?specials=1&ndl=1')

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

    game = [
        game_title,
        release_date,
        original_price,
        final_price,
        review,
        discount_pct,
        datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    ]
    games.append(game)

# Salva os dados em um arquivo CSV
with open('steam_deals2.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(["Titulo", "Data de Lancamento", "Preco Original", "Preco Final", "Analise de Sentimento", "Porcentagem de Desconto", "Data da Consulta"])  # Escreve o cabeçalho
    writer.writerows(games)  # Escreve os dados

print(f"{len(games)} ofertas salvas em steam_deals2.csv")

# Não se esqueça de fechar o driver quando terminar
driver.quit()