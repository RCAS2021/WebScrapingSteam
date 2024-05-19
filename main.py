from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import json
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
    time.sleep(1)  # aguarda o carregamento da página
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# Agora que a página está totalmente carregada, podemos analisá-la com o BeautifulSoup
soup = BeautifulSoup(driver.page_source, 'lxml')

data_body = soup.find_all('div', {'class':'col search_name ellipsis'})
data_released = soup.find_all('div', {'class':'col search_released responsive_secondrow'})
data_prices = soup.find_all('div', {'class':'discount_prices'})
data_reviews = soup.find_all('span', {'class':'search_review_summary'})
data_discount_pct = soup.find_all('div', {'class':'discount_pct'})

games = []

for i in range(len(data_body)):
    prices = data_prices[i].text.strip().split('R$', 2) if i < len(data_prices) else None
    original_price = 'R$' + prices[1].strip().replace('\n', '').replace('\r', '') if prices else None
    final_price = 'R$' + prices[-1].strip().replace('\n', '').replace('\r', '') if prices else None
    
    release_date = data_released[i].text.strip().replace('\n', '').replace('\r', '') if i < len(data_released) else None
    
    review = data_reviews[i]['data-tooltip-html'].split('<br>')[0] if i < len(data_reviews) and data_reviews[i]['data-tooltip-html'] else None
    
    discount_pct = data_discount_pct[i].text.strip() if i < len(data_discount_pct) and data_discount_pct[i].text.strip() else None
    
    game_title = data_body[i].text.strip().replace('\n', '').replace('\r', '') if i < len(data_body) else None

    game = {
        "Título do Jogo": game_title,
        "Data de Lançamento": release_date,
        "Preço Original": original_price,
        "Preço Final": final_price,
        "Análise de Sentimento": review,
        "Porcentagem de Desconto": discount_pct,
        "Data da Consulta": datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    }
    games.append(game)

# Salva os dados em um arquivo JSON
with open('steam_deals2.json', 'w', encoding='utf-8') as f:
    json.dump(games, f, ensure_ascii=False, indent=4)

print(f"{len(games)} ofertas salvas em steam_deals2.json")

# Não se esqueça de fechar o driver quando terminar
driver.quit()