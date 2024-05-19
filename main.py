import bs4 as bs
import urllib.request
import json
from datetime import datetime

# Abre uma conexão
my_url = urllib.request.urlopen('https://store.steampowered.com/search/?specials=1&ndl=1').read()

# Transforma o html em um objeto beautifulsoup
soup = bs.BeautifulSoup(my_url, 'lxml')

data_body = soup.find_all('div', {'class':'col search_name ellipsis'})
data_released = soup.find_all('div', {'class':'col search_released responsive_secondrow'})
data_prices = soup.find_all('div', {'class':'discount_prices'})
data_reviews = soup.find_all('span', {'class':'search_review_summary'})
data_discount_pct = soup.find_all('div', {'class':'discount_pct'})  # Nova linha

games = []

for i in range(len(data_body)):
    prices = data_prices[i].text.strip().split('R$', 2)
    original_price = 'R$' + prices[1].strip().replace('\n', '').replace('\r', '')
    final_price = 'R$' + prices[2].strip().replace('\n', '').replace('\r', '')
    
    release_date = data_released[i].text.strip().replace('\n', '').replace('\r', '') if data_released[i].text.strip() else None
    
    review = data_reviews[i]['data-tooltip-html'].split('<br>')[0] if data_reviews[i]['data-tooltip-html'] else None
    
    discount_pct = data_discount_pct[i].text.strip() if data_discount_pct[i].text.strip() else None  # Nova linha
    
    game = {
        "Título do Jogo": data_body[i].text.strip().replace('\n', '').replace('\r', ''),
        "Data de Lançamento": release_date,
        "Preço Original": original_price,
        "Preço Final": final_price,
        "Análise de Sentimento": review,
        "Porcentagem de Desconto": discount_pct,  # Nova linha
        "Data da Consulta": datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    }
    games.append(game)

# Salva os dados em um arquivo JSON
with open('steam_deals.json', 'w', encoding='utf-8') as f:
    json.dump(games, f, ensure_ascii=False, indent=4)

print(f"{len(games)} ofertas salvas em steam_deals.json")