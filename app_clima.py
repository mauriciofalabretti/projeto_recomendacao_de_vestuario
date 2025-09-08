import streamlit as st
from main import previsao_tempo, CityCompleter
from model import gerar_recomendacao
from prompt_toolkit.document import Document

st.title('Olá, mundo!')
st.write('Bem-vindo ao meu primeiro app com Streamlit.')

sugestoes = CityCompleter()
cidade = st.text_input('Digite a sua cidade: ')
documento_usuario = Document(cidade)


if len(cidade) > 0:
    gerador_sugestoes = sugestoes.get_completions(documento_usuario, None)
    lista_sugestoes = [s.text for s in gerador_sugestoes]
    lista_cidades = st.selectbox("Sugestões de cidades:",lista_sugestoes)
    dados_previsao = previsao_tempo(lista_cidades)
    if "ERRO" not in dados_previsao:
        st.write(f'\n Previsão do Tempo para {lista_cidades} ')
        st.write('-' * 50)
        for i in range(3):  # Laço de repetição de 3 vezes para retornar os 3 dias da API climática
            data = dados_previsao["forecast"]["forecastday"][i]["date"]
            temp_min = dados_previsao["forecast"]["forecastday"][i]["day"]["mintemp_c"]
            temp_max = dados_previsao["forecast"]["forecastday"][i]["day"]["maxtemp_c"]
            condicao = dados_previsao["forecast"]["forecastday"][i]["day"]["condition"]["text"].strip().lower()
            recomendacao = gerar_recomendacao(temp_min, temp_max,
                                              condicao)  # De posse das temperaturas e condição climática, gera uma recomendação para cada um dos dias

            # Estrutura de apresentação dos dados e recomendação
            st.write(f'\nData: {data}')
            st.write(f'Temperatura: min {temp_min}° e máx {temp_max}°')
            st.write(f'Condição: {condicao}\n')
            st.write(f'-----'
                  f'\nRecomendação de Vestuário:\n'
                  f'{recomendacao}')
    else:  # Se houver "ERRO" dentro de `dados_previsao`, vai imprimir a mensagem que a variável guarda
        st.write(dados_previsao)