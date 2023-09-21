from datetime import datetime
import pandas as pd
import numpy as np
import folium
from folium.plugins import MarkerCluster
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from streamlit_folium import folium_static
from PIL import Image


#from utils import general_data as gd
#from utils.process_data import process_data

st.set_page_config(page_title='Fome Zerro!', page_icon='🍽️', layout='wide')


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

def topcuisines(order, clasif):
        top_cuisines = df1_cuisines.loc[:,['Cuisines','Aggregate_rating']].groupby('Cuisines').mean().sort_values('Aggregate_rating', ascending=order).reset_index()
        fig = px.bar(top_cuisines, x='Cuisines', y='Aggregate_rating', title= clasif,
                    text_auto=True, color='Cuisines',
                    labels={'Cuisines':'Colinária',
                     'Aggregate_rating':'Avaliações'})
       
        fig.update_layout(title_x=0.2)
        fig.update_layout(title_font_color='black')

        fig.update_traces(textfont_size=10, textangle=1, textposition="inside", cliponaxis=False)
        return fig

def mel_colinaria (y, i):
    #lins = df1['Cuisines'] == 'Italian'
    cols = ['Country','City', 'Cuisines', 'Average_Cost_for_two', 'Aggregate_rating', 'Currency', 'Name_Restaurant']
    metrica = df1.loc[df1['Cuisines'] == 'Italian',cols].sort_values('Aggregate_rating', ascending=False).reset_index().head(10)

    metrica = round(metrica,2)

    res_colinaria = metrica.iloc[y][i]
   


    return res_colinaria
    
def retornar_ajuda(i):
    cols = ['Country','City', 'Cuisines', 'Average_Cost_for_two', 'Currency', 'Aggregate_rating']
    metrica = df1.loc[df1['Cuisines'] == 'Italian',cols].sort_values('Aggregate_rating', ascending=False).reset_index().head(10)
    ajuda = (f'''
            País:  {metrica["Country"][i]}\n
            Cidade: {metrica["City"][i]}\n
            Prato por dois: {metrica["Average_Cost_for_two"][i]}({metrica["Country"][i]})
''')
    return ajuda
#                      ''')
#  , value= (f'{metrica["Aggregate_rating"][i]}/5.0') 
#  , label_visibility='visible')
#    return res_colinaria

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
st.header('🍽️Visão Colinária!')

image_path = 'PRATO.png'
image = Image.open( 'PRATO.png' )
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

top = st.sidebar.slider(
   "Selecionar a qtd de Restaurantes que desejas visualizar", 1, 20, 10
)

st.sidebar.markdown('''---''')

cuisines = st.sidebar.multiselect(
        "Escolha os Tipos de Culinária ",
        df.loc[:, "Cuisines"].unique().tolist(),
        default=[
            "Home-made",
            "BBQ",
            "Japanese",
            "Brazilian",
            "Arabian",
            "American",
            "Italian",
        ],
    )


st.sidebar.markdown('''---''')
st.sidebar.markdown('### Powered by Comunidade DS')

#linha_selecionada = df1['Order_Date'] < data_slider
#df1 = df1.loc[linha_selecionada,:]
#
# Filtro de Trafico
linha_selecionada = df1['Country'].isin(paises)
df1_country = df1.loc[linha_selecionada,:].head(top)

linha_selecionada = df1['Cuisines'].isin(cuisines)
df1_cuisines = df1.loc[linha_selecionada,:]





#==============================================
# Layout no Streamlit
#==============================================

with st.container():
  
  st.markdown(f'#### Melhores Restaurantes dos principais tipos de Colinária')
 
  #metrica = metrica['Cuisines']
  col1, col2, col3, col4, col5 = st.columns(5, gap="small")
    
  with col1:
    label1 = mel_colinaria(y = 0, i = 7)
    label2 = mel_colinaria(y = 0, i = 3)
    res_colinaria = mel_colinaria(y = 0, i = 5)
    ajuda = retornar_ajuda(i=0)
    col1.metric ( label=(f'{str(label2)}: {""}{label1}'), value = (f'{res_colinaria}/5.0'), help= str(f'{ajuda}'),label_visibility='visible')
  with col2:
    label1 = mel_colinaria(y = 1, i = 7)
    label2 = mel_colinaria(y = 1, i = 3)
    res_colinaria = mel_colinaria(y = 1, i = 5)
    ajuda = retornar_ajuda(i=1)
  col2.metric ( label=(f'{label2 }: {""}{ label1}'), value = (f'{res_colinaria}/5.0'), help= (str(f'{ajuda}')) )
  with col3:
    label1 = mel_colinaria(y = 2, i = 7)
    label2 = mel_colinaria(y = 2, i = 3)
    res_colinaria = mel_colinaria(y = 2, i = 5)
    ajuda = retornar_ajuda(i=2)
    col3.metric ( label=(f'{str(label2)}: {""}{label1}'), value = (f'{res_colinaria}/5.0'), help= (ajuda) )
  with col4:
    label1 = mel_colinaria(y = 3, i = 7)
    label2 = mel_colinaria(y = 3, i = 3)
    res_colinaria = mel_colinaria(y = 3, i = 5)
    ajuda = retornar_ajuda(i=3)
    col4.metric ( label=(f'{str(label2)}: {""}{label1}'), value = (f'{res_colinaria}/5.0'), help= (ajuda) )
  with col5:
    label1 = mel_colinaria(y = 4, i = 7)
    label2 = mel_colinaria(y = 4, i = 3)
    res_colinaria = mel_colinaria(y = 4, i = 5)
    ajuda = retornar_ajuda(i=4)
    col5.metric ( label=(f'{str(label2)}: {label1}'), value = (f'{res_colinaria}/5.0'), help= (ajuda) )

  #st.dataframe(metrica.head(5))

with st.container():
  st.markdown(f'#### Top {top} Restaurantes')
  lins = ['ID_Restaurant', 'Name_Restaurant', 'Country', 'City', 'Cuisines', 'Average_Cost_for_two','Aggregate_rating','Votes']
  mel =df1_country.loc[:,lins].groupby(['ID_Restaurant', 'Name_Restaurant', 'Country', 'City', 'Cuisines']).mean().sort_values('Aggregate_rating', ascending=False).reset_index()
  st.dataframe(mel.head(top))

with st.container():
    
    col1, col2 = st.columns(2)
    with col1:
      fig = topcuisines (order = False, clasif='Top 10 Melhores Tipos de Culinárias')
      st.plotly_chart(fig, use_container_width=True)

      
    with col2:
      fig = topcuisines (order = True, clasif='Top 10 Piores Tipos de Culinárias')
      st.plotly_chart(fig, use_container_width=True)
   
   
      
with st.container():
    st.markdown('---')
    st.markdown('Mapa')
