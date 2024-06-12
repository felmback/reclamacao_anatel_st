import streamlit as st
import plotly.express as px
import pandas as pd
import warnings
import folium
from streamlit_folium import folium_static
# from folium.plugins import MarkerCluster
from folium.plugins import HeatMap
warnings.filterwarnings('ignore')



data_rec = "datasets/Consumidor_Reclamacoes.csv"
data_lat_log ="datasets/lat_log_municipios.xlsx"

df_rec = pd.read_csv(data_rec,sep=';', on_bad_lines='skip')
df_lat = pd.read_excel(data_lat_log)

df_marged = pd.merge(df_rec, df_lat, how='left', left_on='COD_MUNICIPIO', right_on='GEOCODIGO_MUNICIPIO')
df_marged.drop(["GEOCODIGO_MUNICIPIO","Linha","NOME_MUNICIPIO","DATA_EXTRACAO","TIPO_ATENDIMENTO","SERVICO","ANO_MES"], axis=1, inplace=True)


# Resumo geral
st.title('Solicitações registradas na Anatel - SCM (Banda Larga)')
st.write('Este aplicativo fornece uma visão geral das reclamações de registradas.')

ano = st.slider('Selecione um ano', min_value=2022, max_value=2024, value=2024, step=1)
st.checkbox('Mostrar todos os anos', value=True)
st.write('O ano selecionado foi:', ano)
df = df_marged[df_marged['ANO'] == ano]
# Gráfico de barras comparando operadoras por volume
st.header('Comparação de Operadoras por Volume')
operadoras_count = df.groupby(['OPERADORAS'])["SOLICITACOES"].sum().reset_index(name='SOLICITACOES')
operadoras_count.sort_values(by='SOLICITACOES', ascending=True, inplace=True)

fig_operadoras = px.bar(operadoras_count,
                         x='SOLICITACOES', 
                         y='OPERADORAS', 
                         title='Quantidade de Reclamações por Operadora', 
                         labels={'Quantidade': 'Quantidade de Reclamações', 'Operadora': 'Operadora'},
                         orientation="h",
                         color_discrete_sequence=px.colors.sequential.Agsunset
                    
                    )
st.plotly_chart(fig_operadoras)

# Gráfico de barras evidenciando o assunto
st.header('Assuntos das Reclamações')
assuntos_count = df.groupby(['ASSUNTO'])["SOLICITACOES"].sum().reset_index(name='SOLICITACOES')
assuntos_count.sort_values(by='SOLICITACOES', ascending=True, inplace=True)

fig_assuntos = px.bar(assuntos_count, 
                      x='SOLICITACOES',
                      y='ASSUNTO', 
                      title='Quantidade de Reclamações por Assunto', 
                      labels={'Quantidade': 'Quantidade de Reclamações', 'Assunto': 'Assunto'},
                      orientation="h",
                      color_discrete_sequence=px.colors.sequential.Agsunset
                    )
st.plotly_chart(fig_assuntos)

# de calor
st.header('Mapa de Reclamações por Município')
municipios = df.groupby(['LATITUDE', 'LONGITUDE'])["SOLICITACOES"].sum().reset_index(name='SOLICITACOES')

loc_lat = df['LATITUDE'].mean()
loc_long = df['LONGITUDE'].mean()

m = folium.Map(location=[loc_lat,loc_long], zoom_start=3,tiles='CartoDB positron')

heat_data = [[row['LATITUDE'], row['LONGITUDE'], row['SOLICITACOES']] for index, row in municipios.iterrows()]


HeatMap(heat_data,min_opacity=0.4, max_opacity=0.9).add_to(m)

folium_static(m)

#grafico cluster
# m = folium.Map(location=[-15.77972, -47.92972], zoom_start=4)

# marker_cluster = MarkerCluster().add_to(m)

# # Adicionar os marcadores ao cluster
# for idx, row in municipios.iterrows():
#     folium.Marker(
#         location=[row['LATITUDE'], row['LONGITUDE']],
#         popup=f"{row['Quantidade']} reclamações"
#     ).add_to(marker_cluster)

# # Exibir o mapa
# folium_static(m)

# # mapa de marcação
# m = folium.Map(location=[-15.77972, -47.92972], zoom_start=4)

# for idx, row in municipios.iterrows():
#     folium.Marker(
#         location=[row['LATITUDE'], row['LONGITUDE']],  # Substitua por coordenadas reais
#         # popup=f"{row['CIDADE_UF']}: {row['Quantidade']} reclamações"
#     ).add_to(m)

# folium_static(m)

# Tabela resumida por operadora, assunto, problema e quantidade
st.header('Tabela Resumida')
assunto_filter = st.selectbox('Selecione um Assunto', df['ASSUNTO'].unique())
filtered_df = df[df['ASSUNTO'] == assunto_filter]

tabela_resumo = filtered_df.groupby(['OPERADORAS', 'ASSUNTO', 'PROBLEMA']).size().reset_index(name='Quantidade')
st.dataframe(tabela_resumo, use_container_width=True,hide_index=True)


