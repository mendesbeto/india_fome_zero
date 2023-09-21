from datetime import datetime
import pandas as pd
import numpy as np
from folium import Marker, folium
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from streamlit_folium import folium_static
from PIL import Image

st.set_page_config(page_title='Paises', page_icon='🌎', layout='wide')


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


def criar_grafico(df1):
      
      pais_aval = (df1.loc[:,['Country', 'Votes']]
                     .groupby('Country').mean()
                     .sort_values('Votes', ascending=False).reset_index())
      pais_aval = round(pais_aval,2)
      fig = (px.bar(pais_aval, x='Country', y='Votes', title='Média de Avaliações feitas por País',
            text_auto=True,
             labels={'Votes':'Quantidade de Avaliações',
                    'Country' : 'Paises'}))
       
      fig.update_layout(title_x=0.2)
      fig.update_layout(title_font_color='black')

      fig.update_traces(textfont_size=10, textangle=1, textposition="outside", cliponaxis=False)

      return fig
def top_cidades(df1):
  cols = ['Country', 'City' ]
  t10c = df1.loc[:,cols].groupby('Country').nunique().sort_values('City',ascending=False).reset_index()
  t10c = round(t10c,2)
  fig = px.bar(t10c.head(10), x='Country', y= 'City', title='Top 10 Cidades',text_auto=True,
             labels={'City':'Cidades',
                    'Country' : 'Paises'})

  fig.update_layout(title_x=0.2)
  fig.update_layout(title_font_color='black')
  fig.update_traces(textfont_size=10, textangle=1, textposition="outside", cliponaxis=False)

  return fig

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
st.header('🌎 Visão Paises !')

image = Image.open( 'prato_vasio.png' )
st.sidebar.image(image, width=120)

st.sidebar.markdown('# 🍴 Fome Zero !')
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
st.sidebar.markdown('### Powered by Comunidade DS')

# Filtro de Trafico
linha_selecionada = df1['Country'].isin(paises)
df1 = df1.loc[linha_selecionada,:]

#==============================================
# Layout no Streamlit
#==============================================

with st.container():

   cols = ['Country', 'Name_Restaurant' ]
   restaurantes_top = df1.loc[:,cols].groupby('Country').count().sort_values('Name_Restaurant',ascending=False).reset_index()
   restaurantes_top = px.bar(restaurantes_top, x='Country', y='Name_Restaurant', title='Top 10 Restaurantes',text_auto=True,
             labels={'Name_Restaurant':'Restaurantes',
                    'Country' : 'Paises'})

   st.plotly_chart(restaurantes_top, use_container_width=True, theme='streamlit')

with st.container():
   fig = top_cidades(df1)
   st.plotly_chart(fig, use_container_width=True, theme='streamlit')

with st.container():
    col1, col2 = st.columns(2)
    with col1:      
      fig = criar_grafico(df1)
      st.plotly_chart(fig, use_container_width=True, theme='streamlit')

    with col2:
      cols = ['Country','Average_Cost_for_two']
      df2 = round((df1.loc[:,cols].groupby('Country').mean().sort_values('Average_Cost_for_two', ascending=False)).reset_index(),2)
      media_preco = px.bar(df2, x='Country', y='Average_Cost_for_two', title='Média de Preços por País',text_auto=True,
             labels={'Average_Cost_for_two':'Preço de prato para duas pessoas',
                    'Country' : 'Paises'})
      st.plotly_chart(media_preco, use_container_width=True, theme='streamlit')
with st.container():
    st.markdown('---')
