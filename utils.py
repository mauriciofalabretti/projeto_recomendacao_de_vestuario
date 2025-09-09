# Importação de bibliotecas
import requests # Permite fazer requisições HTTP (API calls)
import os # Permite a comunicação com o sistema operacional
from typing import Iterable # Permite que uma função retorne um objeto iterável
from prompt_toolkit.completion import Completer, Completion, CompleteEvent # Habilita o autocomplete
from prompt_toolkit.document import Document # Permite monitorar o input do usuário


# Classe que fornece funcionalidades de autocompletar para cidades
class CityCompleter(Completer):
    # Método que busca sugestões de autocompletar da API com base no input do usuário
    def get_completions(
        _self, input_data: any, complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        """
        -> Busca sugestões de autocompletar para a entrada do usuário
        :param input_data: Recebe a entrada do usuário
        :param complete_event: Recebe o evento que disparou
        :return: Retorna sugestões de autocompletar para o usuário
        """
        if isinstance(input_data, Document): # Se for um objeto da classe, ele usa o Document para monitorar a entrada
            city_name = input_data.get_word_before_cursor()
        else:
            city_name = input_data

        if len(city_name) < 2: # Se o input do usuário for muito pequeno, não há retorno de sugestões
            return []

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
    # Faz a requisição à API climática e realiza o tratamento de exceções para o caso da requisição falhar
    try:
        response = requests.get(url_clima, params={'key': os.getenv("WEATHER_API_KEY"),
                                         'q': local,
                                         'days': 3})

        if response.status_code == 200: # Caso tenha sucesso, converte a resposta em JSON
            dados = response.json()
        else: # Tenta extrair a mensagem de erro da resposta da API para fornecer um feedback mais claro ao usuário
            dados_erro = response.json()
            mensagem_api = dados_erro.get("error", {}).get("message", "Sem mensagem de erro fornecida pela API.") # Tenta extrair a mensagem de erro da resposta da API, se presente. Caso contrário, utiliza uma mensagem padrão
            return {"ERRO": f"ERRO! {response.status_code} - {mensagem_api}"} # Retorna um dicionário com a chave "ERRO", o código do erro e a mensagem obtida
    except requests.exceptions.RequestException:
        return {"ERRO": "ERRO! Não foi possível conectar ao servidor. Verifique sua conexão com a internet."}

    return dados # Se tudo deu certo, retorna os dados
