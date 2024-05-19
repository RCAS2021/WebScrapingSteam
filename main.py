from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import csv
import re
from datetime import datetime

def get_driver(url):
    # Inicia o driver do navegador (neste caso, Chrome)
    driver = webdriver.Chrome()

    # Abre a página
    driver.get(url)

    # Aguarda até que o conteúdo da página seja carregado
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'search_result_row')))

    return driver

def roll_page(driver):
    # Continua rolando até o final da página ou até que não haja mais novos jogos sendo carregados
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(10)  # aguarda o carregamento da página, tempo adicional para evitar muitos requests
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def parse_games(soup):
    # Capturando dados
    data_body = soup.find_all('div', {'class':'col search_name ellipsis'})
    data_released = soup.find_all('div', {'class':'col search_released responsive_secondrow'})
    data_prices = soup.find_all('div', {'class':'discount_prices'})
    data_reviews = soup.find_all('span', {'class':'search_review_summary'})
    data_discount_pct = soup.find_all('div', {'class':'discount_pct'})

    games = []

    # Iterando pelos dados
    for i in range(len(data_body)):
        # Dividindo as strings que vieram em data_prices para pegar cada parte e removendo espaços e quebras de linha
        prices = data_prices[i].text.strip().split('R$', 2) if i < len(data_prices) else None
        original_price = 'R$' + prices[1].strip().replace('\n', '').replace('\r', '') if prices else None
        final_price = 'R$' + prices[-1].strip().replace('\n', '').replace('\r', '') if prices else None

        # Remove 'Preço p/ você:' do preço original, se estiver presente
        if original_price and 'Preço p/ você:' in original_price:
            original_price = original_price.replace('Preço p/ você:', '').strip()

        # Removendo espaços e quebras de linha
        release_date = data_released[i].text.strip().replace('\n', '').replace('\r', '') if i < len(data_released) else None

        positive_review_pct = 0
        total_reviews = 0

        # Pegando as partes da porcentagem de reviews e total de reviews a partir da string
        if i < len(data_reviews) and data_reviews[i].has_attr('data-tooltip-html'):
            tooltip_html = data_reviews[i]['data-tooltip-html']
            match = re.search(r'(\d+)% das? (\d{1,3}(?:\,\d{3})*) análises', tooltip_html)
            if match:
                positive_review_pct = int(match.group(1))
                total_reviews = int(match.group(2).replace(',', ''))
            else:
                positive_review_pct = 0
                total_reviews = 0

        # Retirando espaços em branco
        discount_pct = data_discount_pct[i].text.strip() if i < len(data_discount_pct) and data_discount_pct[i].text.strip() else None

        # Converte a porcentagem de desconto para um número inteiro
        discount = int(discount_pct.replace('%', '')) if discount_pct else 0

        # Filtrando os jogos
        if discount <= -50 and total_reviews > 500 and positive_review_pct >= 60:
            # Adicionando símbolo de %
            positive_review_pct = f'{positive_review_pct}%' 

            # Retirando espaços em branco e quebras de linha
            game_title = data_body[i].text.strip().replace('\n', '').replace('\r', '') if i < len(data_body) else None

            # Criando lista com informações do jogo
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
            # Adicionando lista com informações do jogo à lista de jogos
            games.append(game)

            # Parando o programa se a porcentagem de análises positivas chegar a menos que 60%
        elif positive_review_pct < 60:
            print('Porcentagem de análises positivas menor do que 60. Terminando.')
            break

    return games

def save_to_csv(games, filename):
    # Salva os dados em um arquivo CSV
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Titulo", "Data de Lancamento", "Preco Original", "Preco Final", "Porcentagem Analises Positivas", "Porcentagem de Desconto", "Total de Reviews", "Data da Consulta"])  # Escreve o cabeçalho
        writer.writerows(games)  # Escreve os dados

    print(f"{len(games)} ofertas salvas em {filename}")

def get_soup(url):
    # Pega o driver do Chrome
    driver = get_driver(url)

    # Rola a página até o final
    roll_page(driver)

    # Agora que a página está totalmente carregada, podemos analisá-la com o BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'lxml')

    # Coleta os jogos
    games = parse_games(soup)

    # Salva os jogos em arquivo csv
    save_to_csv(games, 'steam_deals.csv')

    # Fecha o driver quando terminar
    driver.quit()

def main():
    url = 'https://store.steampowered.com/search/?sort_by=Reviews_DESC&specials=1&ndl=1'
    get_soup(url)

if __name__ == "__main__":
    main()
