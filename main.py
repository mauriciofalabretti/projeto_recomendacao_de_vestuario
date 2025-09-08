# Importação de bibliotecas
import requests # Permite fazer requisições HTTP (API calls)
import os # Permite a comunicação com o sistema operacional
import streamlit as st
from typing import Iterable # Permite que uma função retorne um objeto iterável
from prompt_toolkit import prompt # Permite a captura avançada de input
from prompt_toolkit.completion import Completer, Completion, CompleteEvent # Habilita o autocomplete
from prompt_toolkit.document import Document # Permite monitorar o input do usuário
from model import gerar_recomendacao # Estabelece a conexão com o modelo de IA presente em model.py



# Classe que fornece funcionalidades de autocompletar para cidades
class CityCompleter(Completer):
    # Método que busca sugestões de autocompletar da API com base no input do usuário
    @st.cache_data
    def get_completions(
        _self, _document: Document, complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        """
        -> Busca sugestões de autocompletar para a entrada do usuário
        :param document: Monitora a entrada do usuário no prompt
        :param complete_event: Recebe o evento que disparou
        :return: Retorna sugestões de autocompletar para o usuário
        """

        city_name = _document.get_word_before_cursor()
        if len(city_name) < 2: # Se o input do usuário for muito pequeno, não há retorno de sugestões
            return

        # URL da API geográfica para buscar os nomes das cidades
        url_geo = f"http://geodb-free-service.wirefreethought.com/v1/geo/cities?limit=5&namePrefix={city_name}&countryIds=BR"

        # Lida com erros de requisição da API para evitar que o programa pare de funcionar
        try:
            response = requests.get(url_geo)
            if response.status_code == 200: # Caso tenha sucesso, transforma a resposta em JSON
                dados = response.json()
                sugestoes_completas = []
                for city in dados["data"]: # Laço de repetição para cada cidade dentro da chave especificada
                    nome = f"{city['name']}, {city['country']}" # Para cada cidade, armazena seu nome e país na variável `nome`
                    sugestoes_completas.append(Completion(nome, start_position=-len(city_name))) # Gera uma sugestão de autocompletar para o prompt_toolkit
                return sugestoes_completas
        except requests.exceptions.RequestException as e: # Exceção para erro de requisição
            pass
        except requests.exceptions.JSONDecodeError as e: # Exceção para erro da decodificação do JSON
            pass


# URL da API para previsão do tempo
url_clima = "http://api.weatherapi.com/v1/forecast.json"


# Função para buscar a informação da previsão do tempo
def previsao_tempo(local: str):
    """
    -> Busca os dados da API climática através de requisição
    :param local: Cidade informada pelo usuário
    :return: Retorna a previsão do tempo para a cidade escolhida
    """
    response = requests.get(url_clima, params={'key': os.getenv("WEATHER_API_KEY"),
                                         'q': local,
                                         'days': 3})

    if response.status_code == 200: # Caso tenha sucesso, converte a resposta em JSON
        dados = response.json()
    else:
        try: # Tenta extrair a mensagem de erro da resposta da API para fornecer um feedback mais claro ao usuário
            dados_erro = response.json()
            mensagem_api = dados_erro.get("error", {}).get("message", "Sem mensagem de erro fornecida pela API.") # Tenta extrair a mensagem de erro da resposta da API, se presente. Caso contrário, utiliza uma mensagem padrão
            return {"ERRO": f"ERRO! {response.status_code} - {mensagem_api}"} # Retorna um dicionário com a chave "ERRO", o código do erro e a mensagem obtida
        except requests.exceptions.JSONDecodeError:
            return {"ERRO": f"ERRO! {response.status_code} - {response.text}"}

    return dados # Se tudo deu certo, retorna os dados


# Programa Principal
if __name__ == "__main__":

    cidade = prompt("Digite a cidade: ", completer=CityCompleter()) # Utiliza o prompt para capturar a entrada do usuário e passá-la para o completer fazer a sugestão
    dados_previsao = previsao_tempo(cidade) # Armazena o retorno da função `previsao_tempo` para que possa extrair as informações desejadas para a IA

    # Verifica a existência de erros dentro da resposta da API climática para evitar a execução desnecessária de código
    if "ERRO" not in dados_previsao:
        print(f'\n Previsão do Tempo para {cidade} ')
        print('-' * 50)
        for i in range(3): # Laço de repetição de 3 vezes para retornar os 3 dias da API climática
            data = dados_previsao["forecast"]["forecastday"][i]["date"]
            temp_min = dados_previsao["forecast"]["forecastday"][i]["day"]["mintemp_c"]
            temp_max = dados_previsao["forecast"]["forecastday"][i]["day"]["maxtemp_c"]
            condicao = dados_previsao["forecast"]["forecastday"][i]["day"]["condition"]["text"].strip().lower()
            recomendacao = gerar_recomendacao(temp_min, temp_max, condicao) # De posse das temperaturas e condição climática, gera uma recomendação para cada um dos dias

            # Estrutura de apresentação dos dados e recomendação
            print(f'\nData: {data}')
            print(f'Temperatura: min {temp_min}° e máx {temp_max}°')
            print(f'Condição: {condicao}\n')
            print(f'-----'
                  f'\nRecomendação de Vestuário:\n'
                  f'{recomendacao}')
    else: # Se houver "ERRO" dentro de `dados_previsao`, vai imprimir a mensagem que a variável guarda
        print(dados_previsao)
