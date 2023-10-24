#Painel de indicadores econômicos usando streamlit

#set light theme as default e wide screen enable

#Pacotes necessários

import pandas as pd             # manipulação dos dados tabulares e scraping
import numpy as np              # manipulação séries temporais
import ssl                      # conexão de segurança http
import datetime as dt           # manipulação de objetos com data
import urllib                   # pacote para requerimento de download
import matplotlib.pyplot as plt # pacote para criar gráficos
import openpyxl as oxl          # pacote para manipulação de arquivos .xlsx (preenchimento)
import requests                 # pacote para requisitar informações por API
from dateutil.relativedelta import relativedelta # pacote para realizar operações com datas
from bs4 import BeautifulSoup as BS # pacote para scraping
import plotly.io as pio
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

#Importação de dados

## Dados do IPCA (Variação Mensal, Acumulado no Ano e Acumulado em 12 Meses)

data_atual = dt.datetime.now() # captura data para determinar período na consulta da API
ipca_brasil = requests.get(f'https://apisidra.ibge.gov.br/values/t/7060/n1/all/v/63,69,2265/p/202201-{data_atual.year}{data_atual.month-1}/c315/7169/d/v63%202')
ipca_brasil = ipca_brasil.json()
ipca_brasil = pd.DataFrame(ipca_brasil)

## Tratamento dos dados do IPCA (Variação Mensal, Acumulado no Ano e Acumulado em 12 Meses)

ipca_brasil.columns = ipca_brasil.iloc[0] 
ipca_brasil = ipca_brasil[1:]
ipca_brasil['Valor'] = ipca_brasil['Valor'].astype(float)
ipca_brasil['Mês (Código)'] = pd.to_datetime(ipca_brasil['Mês (Código)'], format='%Y%m')

ipca_brasil = pd.crosstab(ipca_brasil['Mês (Código)'], ipca_brasil['Variável'], ipca_brasil['Valor'], aggfunc='sum')

coluna_ordem = ['IPCA - Variação mensal', 'IPCA - Variação acumulada em 12 meses', 'IPCA - Variação acumulada no ano']

ipca_brasil = ipca_brasil.reindex(coluna_ordem, axis=1)

ipca_brasil_94_21 = pd.read_feather('ipca_brasil_94_21.feather')

ipca_brasil_94_21.set_index('Mês', inplace=True)

ipca_brasil = pd.concat([ipca_brasil_94_21, ipca_brasil], axis=0)

#Datas para capturar  variação mais atual e anterior.


data_referencia = dt.datetime.now()
data_atual = data_referencia - relativedelta(months=1)
data_anterior = data_referencia - relativedelta(months=2)
data_atual = data_atual.strftime('%Y/%m')
data_anterior = data_anterior.strftime('%Y/%m')

ano_atual = dt.datetime.now().year
meses_ano_atual = pd.date_range(start=f'{ano_atual}-01-01', end=f'{ano_atual}-12-01', freq='MS')

st.set_page_config(layout="wide", page_icon=":bar_chart:", page_title="Indicadores Econômicos")


st.title('Indicadores Econômicos')
st.subheader('**Inflação**')





#Cria três colunas
col1, col2, col3 = st.columns([25, 50, 20])

#Dados filtrados 

#Texto explicativo
with col1:
    st.subheader('**IPCA- ÍNDICE NACIONAL DE PREÇOS AO CONSUMIDOR**')
    st.markdown('O IPCA está relacionado ao processo de reposicionamento tarifário (reajuste ou revisão) dos serviços públicos regulados pela Agepar no que se refere ao manejo de resíduos sólidos, as travessias marítimas e aos serviços de saneamento, abastecimento de água e tratamento de esgoto.  O índice tem por objetivo medir a inflação de um conjunto de produtos e serviços comercializados no varejo, referentes ao consumo pessoal das famílias com rendimentos mensais de 1 a 40 salários mínimos. Esta faixa de renda foi criada com o objetivo de garantir uma cobertura de 90% das famílias pertencentes às áreas urbanas de cobertura do SNIPC (Sistema Nacional de Índices de Preços ao Consumidor). ')

#Gráfico
with col3:

    #create a slider filter to select the year to be displayed

    ano_inicial, ano_final = st.slider(
        "Qual período deseja visualizar?",
        min_value=ipca_brasil.index.min().year,
        max_value=ipca_brasil.index.max().year,
        step=1,
        value=((ipca_brasil.index.max().year-5, ipca_brasil.index.max().year)),
    )

    serie_escolha = st.selectbox(
        "Qual variação você gostaria de visualizar?",
        ("Todas", "Mensal", "Acumulada 12 Meses", "Acumulada no Ano"),
    )


filtered_df = ipca_brasil[(ipca_brasil.index.year >= ano_inicial) & (ipca_brasil.index.year <= ano_final)]
# -- Apply the continent filter
if serie_escolha == "Todas":
    filtered_df = filtered_df[['IPCA - Variação mensal', 'IPCA - Variação acumulada em 12 meses', 'IPCA - Variação acumulada no ano']]
elif serie_escolha == "Mensal":
    filtered_df = filtered_df[['IPCA - Variação mensal']]
elif serie_escolha == "Acumulada 12 Meses":
    filtered_df = filtered_df[['IPCA - Variação acumulada em 12 meses']]
elif serie_escolha == "Acumulada no Ano":
    filtered_df = filtered_df[['IPCA - Variação acumulada no ano']]

#Filtro
with col2:
    #centralize text on column 
    
    #st.text('**EVOLUÇÃO DO ÍNDICE DE INFLAÇÃO IPCA MENSAL, ACUMULADO NO ANO E NOS ÚLTIMOS 12 MESES – NACIONAL**', )
#st.image("streamlit.png", width=200)
# -- Put the title in the last column

    fig = px.line(
        filtered_df, 
        x=filtered_df.index, 
        y=filtered_df.columns.to_list(),
        title='Evolução do índice de inflação IPCA mensal, acumulado no ano e nos últimos 12 meses no Brasil',)

    fig.update_layout(
        
        title={
            'y':1,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
        xaxis_title="Mês",
        yaxis_title="Variação (%)",
        autosize=False,
        width=875,
        height=400,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ),
        legend_title="Variação",
        margin={'t':25,'l':0,'b':0,'r':0} #zera os espaços em branco do gráfico

    )

    st.plotly_chart(fig)