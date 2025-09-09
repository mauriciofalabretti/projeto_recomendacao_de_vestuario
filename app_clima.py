import streamlit as st # Permite criar a interface visual
from datetime import datetime # Permite acessar o horário atual
from model import gerar_recomendacao # Necessário para buscar as recomendações do modelo de IA
from utils import CityCompleter, previsao_tempo # Necessário para gerar sugestões e buscar dados climáticos


# Função para geração de sugestões
@st.cache_data
def get_cached_completions(city: str):
    """
    -> Cria um objeto CityCompleter para acessar a funcionalidade autocompletar da classe e sugerir opções para o usuário
    :param city: Recebe a cidade escolhida pelo usuário
    :return: Retorna sugestões baseadas no input do usuário
    """
    sugestao = CityCompleter()
    gerador_sugestoes = sugestao.get_completions(city, None)

    return gerador_sugestoes


# Interface visual e lógica do aplicativo
hora = datetime.now()

# Personaliza a saudação baseado no horário
if  00 <= hora.hour < 12:
    st.title('Bom dia!')
elif 12 <= hora.hour < 19:
    st.title('Boa tarde!')
else:
    st.title('Boa noite!')

st.write('Bem-vindo(a) ao seu aplicativo de recomendação de vestuário para a previsão do tempo')

# Entrada de dados do usuário
cidade = st.text_input('Digite a sua cidade: ')

# Se o campo cidade tiver conteúdo, então é chamada a função para gerar sugestões baseadas no que foi digitado
if len(cidade) > 0:
    sugestao_cidade = get_cached_completions(cidade)

    # Se as sugestões não estiverem vazias, usa o list comprehension para armazenar as opções geradas
    if sugestao_cidade is not None:
        lista_sugestoes = [s.text for s in sugestao_cidade]

        # Bloco para apresentar os botões de sugestão para o usuário escolher
        st.write("Sugestões de cidades:")
        for i, sugestao in enumerate(lista_sugestoes):
            if st.button(sugestao, key=f'{sugestao}_{i}'): # Cada botão recebe o nome da cidade sugerida e sua respectiva chave na lista para identificação única
                st.session_state['cidade_escolhida'] = sugestao # Armazena a cidade no cache para que seja registrada a escolha do usuário
                st.markdown(f"<span style ='color:aquamarine'>Você escolheu: {sugestao}</span>", unsafe_allow_html=True)

        if st.button('Limpar'): # Se o botão limpar for acionado, limpa o cache e o usuário pode escolher novamente
            del st.session_state['cidade_escolhida']

    # Bloco para buscar os dados da API climática e a recomendação do vestuário pela IA baseado no input do usuário e informações recebidas
    if 'cidade_escolhida' in st.session_state:
        dados_previsao = previsao_tempo(st.session_state.cidade_escolhida)

        # Se função de previsão do tempo obteve êxito na requisição à API, o programa está apto a prosseguir
        if "ERRO" not in dados_previsao:
            st.divider()
            st.write(f'\n Previsão do Tempo para {st.session_state.cidade_escolhida} ')
            for i in range(3):  # Laço de repetição de 3 vezes para retornar os 3 dias da API climática
                data = dados_previsao["forecast"]["forecastday"][i]["date"]
                temp_min = dados_previsao["forecast"]["forecastday"][i]["day"]["mintemp_c"]
                temp_max = dados_previsao["forecast"]["forecastday"][i]["day"]["maxtemp_c"]
                condicao = dados_previsao["forecast"]["forecastday"][i]["day"]["condition"]["text"].strip().lower()

                recomendacao = gerar_recomendacao(temp_min, temp_max,
                                                  condicao)  # De posse das temperaturas e condição climática, gera uma recomendação para cada um dos dias

                # Estrutura de apresentação dos dados e recomendação
                st.divider()
                st.write(f'Data: {data}')
                st.write(f'Temperatura: min {temp_min}° e máx {temp_max}°')
                st.write(f'Condição: {condicao}')
                st.write(f'-----'
                      f'\nRecomendação de Vestuário:\n'
                      f'{recomendacao}')
        else:  # Se houver "ERRO" dentro de `dados_previsao`, vai imprimir a mensagem que a variável guarda
            st.write(dados_previsao)
