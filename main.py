# Importação de bibliotecas e funções
from prompt_toolkit import prompt # Permite a captura avançada de input
from model import gerar_recomendacao # Estabelece a conexão com o modelo de IA presente em model.py
from utils import CityCompleter, previsao_tempo # Permite gerar sugestões para o input do usuário e encaminhá-lo para buscar dados climáticos


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
