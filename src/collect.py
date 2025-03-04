#%%
import requests
import json
# import pandas as pd
import polars as pl
from tqdm import tqdm
from bs4 import BeautifulSoup
#%%
def get_content(url: str) -> requests.Response:
    """
    Função que recebe uma url e retorna o conteúdo da página
    fazendo uma requisição GET. A função utiliza o arquivo
    'headers.json' para passar headers para a requisição.

    param: url -  str com a url da página
    return: objeto requests.Response com o conteúdo da página
    """
    with open('headers.json', 'r') as file:
        headers = json.load(file)

    # fazendo a requisição
    resp = requests.get(url, headers=headers)
    return resp
#%%
def get_basics_info(soup: BeautifulSoup) -> dict:
    """
    Função que recebe um objeto BeautifulSoup e retorna um dicionário com as informações básicas
    de um personagem da série Resident Evil.

    A função extrai as informações da página, que estão contidas em um elemento <div> com a classe
    'td-page-content', e as guarda em um dicionário.

    As informações extraídas são:
        - Nome
        - Sobrenome
        - Ano de nascimento
        - Data de morte
        - Nacionalidade
        - Ocupação

    Retorna um dicionário com as informações extraídas.
    """
    # podemos agora fazer buscas nessa estrutura
    # para fazer buscas, usamos o método find
    # passamos a tag que queremos buscar e a classe que ela tem
    div_page = soup.find('div', class_='td-page-content')

    # podemos encadear os métodos
    # paragrafo = div_page.find_all('p')[1]\
    #                     .find_all('em')

    # pega apenas o paragrafo do indice 1. 'p' é a tag de 'paragrafo'                    
    paragrafo = div_page.find_all('p')[1]
    
    # pega tudo com a tag 'em'. Aqui temos um iteravel, no formato de lista
    ems = paragrafo.find_all('em')

    # estruturando um dicionario com as informações
    data = {}

    for info in ems:
        # info.text.split(':') retorna uma lista de 2 elementos, correspondendo a chave e ao valor
        # que já fazemos o unpacking
        chave, valor, *_ = info.text.split(':')
        
        # removendo os espacos em branco e os '.' do valor
        chave = chave.strip()
        valor = valor.replace('.', '').strip()

        # guardando no dicionario
        data[chave] = valor

    return data
#%%
def get_appearances(soup: BeautifulSoup) -> list:
    """Pega as aparições de um personagem.
    
    Recebe um objeto BeautifulSoup e pega todas as li's que estejam 
    dentro de um h4 com o texto 'Aparições'.
    
    Retorna uma lista com as aparições do personagem.
    """
    # se eu uso parenteses, consigo encadear metodos em linhas diferentes, igual usando o operador '/'
    lis = (soup.find('div', class_='td-page-content')
               .find('h4')
               .find_next()
               .find_all('li'))

    # criando a lista de aparicoes
    aparicoes = [li.text for li in lis]
    return aparicoes
#%%
def get_links() -> list:
    
    # pegando as urls de cada personagem da serie
    base_url = 'https://www.residentevildatabase.com/personagens/'
    response = get_content(base_url)

    # lista com a url de todos os personagens
    soup_links = (BeautifulSoup(response.text, 'html.parser').find('div', class_='td-page-content')
                                                             .find_all('a'))

    links = [link['href'] for link in soup_links]

    return links
#%%
def collect_data(url: str) -> dict:
    """
    Função que recebe uma url e retorna um dicionário com as informações do personagem.

    A função faz uma requisição GET para a url passada, verifica se a requisição foi bem sucedida,
    e caso tenha sido, extrai as informações básicas do personagem e suas aparições
    e retorna um dicionário com as informações.

    Caso a requisição tenha falhado, a função retorna um dicionário vazio.

    param: url - str com a url da página do personagem
    return: dicionário com as informações do personagem
    """
    response = get_content(url)

    if response.status_code == 200:
        print(f'Requisição bem sucedida para url = {url}.')
        
        # pegando o html e convertendo em um objeto inspecionável pelo Python
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')

        # pegando as informacoes basicas do personagem
        data_basics = get_basics_info(soup)

        # buscando as aparicoes e add no dicionario
        data_basics['Appearances'] = get_appearances(soup)
        return data_basics

    else:
        print(f'Erro na requisição: {response.status_code}')
        return {}
#%%

url_list = get_links()

# lista para guardar os dicionarios de infos de cada personagem
data = []

# a funcao tqdm cria uma barra de progresso na tela
# ela re
# cebe como argumento um iteravel
for url in tqdm(url_list):
    # pega o dado para cada personagem e retorna num dict
    dict_character = collect_data(url)

    # quebra a url e pega o nome do personagem, que fica entre as 
    # duas ultimas barras
    character_name = url.split('/')[-2].replace('-', ' ')

    # adiciona chave Name com o nome do personagem
    dict_character['Name'] = character_name

    # adiciona chave URL com o link do personagem
    dict_character['URL'] = url

    # adiciona o dict a lista
    data.append(dict_character)

#%%
df = pl.DataFrame(data)
df.head()