from datetime import datetime
import pandas as pd
import numpy as np
from folium.plugins import MarkerCluster
import folium
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from streamlit_folium import folium_static
from PIL import Image
import locale

st.set_page_config(page_title='Home', page_icon='🏠', layout='wide')


# ============================================================
# Funções
# ============================================================
def clean_code(df1):
    df1['Country Code'] = df1['Country Code'].apply(country_name)
    df1['Rating color'] = df1['Rating color'].apply(color_name)
    df1['Price range'] = df1.apply(lambda x: create_price_tye(x['Price range']), axis = 1)
    #Categorizar por somente um tipo de culinária
    df1["Cuisines"] = df1.loc[:, "Cuisines"].astype (str).apply(lambda x: x.split(",")[0])

    df1 = df1.rename(columns={'Restaurant ID':'ID_Restaurant'})
    df1 = df1.rename(columns={'Restaurant Name':'Name_Restaurant'})
    df1 = df1.rename(columns={'Country Code':'Country'})
    df1 = df1.rename(columns={'Locality Verbose':'Locality_Verbose'})
    df1 = df1.rename(columns={'Average Cost for two':'Average_Cost_for_two'})
    df1 = df1.rename(columns={'Has Table booking':'Has_Table_booking'})
    df1 = df1.rename(columns={'Has Online delivery':'Has_Online_delivery'})
    df1 = df1.rename(columns={'Is delivering now':'Is_delivering_now'})
    df1 = df1.rename(columns={'Switch to order menu':'Switch_to_order_menu'})
    df1 = df1.rename(columns={'Price range':'Price_range'})
    df1 = df1.rename(columns={'Aggregate rating':'Aggregate_rating'})
    df1 = df1.rename(columns={'Rating color':'Rating_color'})
    df1 = df1.rename(columns={'Rating text':'Rating_text'})

    df1 = df1.dropna (subset=['Cuisines']) # Retirumos as Linhas NaN da coluna que possut os valores ausentes e gravamos no própria dataframe copiado
    #df1.isnull().sum() #exibindo o resultado após o drop de valor ausente
    df1 = df1.reset_index()
    del df1['index']
    #Verificando valores duplicados
    #df1 = dfl,duplicated().Sum() # Com esta função verificamos que há 583 valores duplicados Removendo os valores duplicados e deixando apenas a primeira ocorrência. Realizamos também o reset do index
    df1 = df1.drop_duplicates().reset_index()
    del df1['index']

    return df1

def color_name(color_code):
   return COLORS[color_code]

def country_name(country_id):
   return COUNTRIES[country_id]

#Criação do Tipo de Categoria de Comida
def create_price_tye(price_range):
  if price_range == 1:
    return "cheap"
  elif price_range == 2:
    return "normal"
  elif price_range == 3:
    return "expensive"
  else:
    return "gourmet"
  



#Preenchimento do nome dos países
COUNTRIES = {
1: "India",
14: "Australia",
30: "Brazil",
37: "Canada",
94: "Indonesia",
148: "New Zeland",
162: "Philippines",
166: "Qatar",
184: "Singapure",
189: "South Africa",
191: "Sri Lanka",
208: "Turkey",
214: "United Arab Emirates",
215: "England",
216: "United States of America",
}
#Criação do nome das Cores
COLORS = {
"3F7E00": "darkgreen",
"5BA829": "green",
"9ACD32": "lightgreen",
"CDD614": "orange",
"FFBA00": "red",
"CBCBC8": "darkred",
"FF7800": "darkred",
}





df = pd.read_csv('zomato.csv')
df1 = clean_code(df)

#==============================================
# Barra Lateral 
#==============================================
st.header(' 🍴 Fome Zerro !!!')

image = Image.open( 'prato_vasio.png' )
st.sidebar.image(image, width=120)

st.sidebar.markdown('# 🍴 Fome Zero')
st.sidebar.markdown('''___''')
paises = st.sidebar.multiselect(
    "Selecionar País",
    (["India", "Australia", "Brazil", "Canada", 
      "Indonesia", "New Zeland", "Philippines",
      "Qatar", "Singapure", "South Africa", "Sri Lanka", 
      "Turkey", "United Arab Emirates", 
       "England", "United States of America",]),
    default=["Australia", "Brazil", "Canada",
       "Qatar", "South Africa", "England"])

st.sidebar.markdown('''---''')
st.sidebar.markdown('#### Dados Tratados')

@st.cache_data
def convert_df(df1):
    # Converter o dataframe em um arquivo CSV
    return df1.to_csv().encode('utf-8')

csv = convert_df(df1)


st.sidebar.download_button(
    label="Download",
    data=csv,
    file_name='dados.csv',
    mime='text/csv')

st.sidebar.markdown('''---''')
st.sidebar.markdown('### Powered by Comunidade DS')

#linha_selecionada = df1['Order_Date'] < data_slider
#df1 = df1.loc[linha_selecionada,:]
#
# Filtro de Trafico
linha_selecionada = df1['Country'].isin(paises)
df1_sidebar = df1.loc[linha_selecionada,:]

#==============================================
# Layout no Streamlit
#==============================================

with st.container():
    st.markdown('### O Melhor lugar para encontrar o seu mais novo Restaurante fvorir')
    st.markdown('#### Temos as seguintes marcas dentro da nossa Plataforma')
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        restaurantes = len(df1['ID_Restaurant'].unique())
        col1.metric('Restaurantes', restaurantes)
    with col2:
       paises = len(df1['Country'].unique())
       col2.metric('Paises', paises)
    with col3:
       cidades = len(df1['City'].unique())
       col3.metric('Cidades', cidades)
    with col4:
       avaliacao = sum(df1['Votes'])
       col4.metric('Avaliações', avaliacao)
    with col5:
       colinaria = len(df1['Cuisines'].unique())
       col5.metric('Colinárias', colinaria)
with st.container():
    st.write ('#### 🌎 Mapa com a Localização dos restaurantes')

criet_map = (df1.loc[:, ['City', 'Aggregate_rating', 'Currency', 'Cuisines', 'Rating_color', 'ID_Restaurant','Latitude', 'Longitude', 'Average_Cost_for_two', 'Name_Restaurant']]
             .groupby(['City', 'Cuisines','Rating_color', 'Currency', 'ID_Restaurant', 'Name_Restaurant'])
             .median().reset_index())


mapa = folium.Map()
marker_cluster = folium.plugins.MarkerCluster().add_to(mapa)

                    
for i in range ( len (criet_map) ):
   popup_html = f'<div style="width: 350px;">' \
                 f"<b>{criet_map.loc[i, 'Name_Restaurant']}</b><br><br>" \
                 \
                 f"Preço para dois: {criet_map.loc[i, 'Average_Cost_for_two']:.2f} ( {criet_map.loc[i, 'Currency']})<br> " \
                 f"Type: {criet_map.loc[i, 'Cuisines']}<br>" \
                 f"Nota: {criet_map.loc[i, 'Aggregate_rating']}/5.0" \
                 f'</div>'
   folium.Marker([criet_map.loc[i, 'Latitude'], criet_map.loc[i, 'Longitude']],
                   popup=popup_html, width=700, height=300, tooltip='clique aqui', parse_html=True,  
                   zoom_start=30, tiles= 'Stamen Toner', 
                   icon=folium.Icon(color=criet_map.loc[i, 'Rating_color'] , icon='home')).add_to(marker_cluster)
    
folium_static(mapa)


    
