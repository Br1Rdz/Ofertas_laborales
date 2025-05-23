import streamlit as st 
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.dataframe_explorer import dataframe_explorer
# from streamlit_extras.badges import badge
import pandas as pd
import geopandas as gpd
import numpy as np
import folium
from streamlit_folium import st_folium
import time
import nltk
import plotly.express as px
from sklearn.cluster import KMeans
# from sklearn.metrics import pairwise_distances_argmin_min
import sklearn.cluster as cluster
# import sklearn.metrics as metrics
# nltk.download('punkt_tab')
# from sklearn.linear_model import LinearRegression
import joblib

APP_TITLE = 'Ofertas laborales en México'
APP_SUB_TITLE = ':briefcase: Fuente de OCC y Computrabajo'

# ----------------- Uso de app -------------------
# https://docs.streamlit.io/develop/api-reference/write-magic/st.write_stream
def response_generator(texto):
    '''Esta funcion es para mostrar texto letra por letra con un retraso'''
    for letra in texto.split():
        yield letra + " "
        time.sleep(0.1)  

# ----------------- FILTRADO -------------------
def base_filtrada(df):
    '''Esta funcion realiza filtros a la base de datos a partir de los requerimentos del usuario'''
    #Lista de estados
    # lista_estados = [''] + list(df['Estado'].unique())
    # lista_estados.sort()
    # Estado = st.sidebar.selectbox('Estado', lista_estados)
    
    #Lista de requisitos
    # lista_requisitos = [''] + list(df['Experiencia'].unique())
    # lista_requisitos.sort()
    # Requisito = st.sidebar.selectbox('Experiencia', lista_requisitos)
    
    #Lista de sueldos
    # https://stackoverflow.com/questions/45695373/removing-a-nan-from-a-list
    # lista_sueldos = [''] + list(df['Sueldo'].dropna().unique())
    # lista_sueldos.sort()
    # Sueldo = st.sidebar.selectbox('Sueldo', lista_sueldos)
    
    lista_laboral = [''] + list(df['Relación_profesional'].unique())
    lista_laboral.sort()
    Campo_laboral = st.sidebar.selectbox(':round_pushpin: Relación profesional', lista_laboral)
    # Campo_laboral = st.radio('Seleccion Relacion profesional:', lista_laboral, horizontal=True)
    
    # https://stackoverflow.com/questions/75988547/display-a-range-of-numbers-with-a-slider-in-streamlit
    # df = df[(df['Experiencia'] == Requisito) & (df['Sueldo'] == Sueldo)]   
    # if Estado:
    #     df = df[df['Estado'] == Estado]
        
    # if Requisito:
    #     df = df[df['Experiencia'] == Requisito]  
        
    # if Sueldo:
    #     df = df[df['Sueldo'] == Sueldo]   
        
    if Campo_laboral:
        df = df[df['Relación_profesional'] == Campo_laboral]      
    
    ##Muestra la tabla
    # st.write(df.shape)
    # st.dataframe(df, hide_index=True)
    # st.markdown(df.style.hide(axis="index").to_html(), unsafe_allow_html=True)
    # st.write(df['Estado'].unique()) 
    
    #numero de filas con coencidencia
    numero = len(df)
    
    if Campo_laboral:
        st.subheader(f':clipboard: {numero} ofertas laborales para {Campo_laboral}', divider="gray")

    return df, Campo_laboral

# ----------------- Metrica -------------------
# def sueldo_min_max_estado(df):
#     for estado, sueldo in zip(df['Estado'],df['Sueldo']):
#         if sueldo == min(df['Sueldo']):
#             sueldo_minimo = sueldo
#             estado_minimo = estado
#         elif sueldo == max(df['Sueldo']):
#             sueldo_maximo = sueldo
#             estado_maximo = estado
#     return sueldo_minimo, estado_minimo, estado_maximo, sueldo_maximo  

@st.cache_data
def sueldo_min_max_estado(df):
    sueldo_minimo = 0
    estado_minimo = "No disponible"
    sueldo_maximo = 0
    estado_maximo = "No disponible"
    
    if not df.empty and 'Estado' in df.columns and 'Sueldo' in df.columns:
        for estado, sueldo in zip(df['Estado'], df['Sueldo']):
            if sueldo == min(df['Sueldo']):
                sueldo_minimo = sueldo
                estado_minimo = estado
            elif sueldo == max(df['Sueldo']):
                sueldo_maximo = sueldo
                estado_maximo = estado
                
    return sueldo_minimo, estado_minimo, estado_maximo, sueldo_maximo

# def ingreso_mensual(df, filtro):
#     sueldo_ingreso = []
#     for i, j in zip(df['Estado'], df['Ingreso_mensual']):
#         if i == filtro:
#             sueldo_ingreso.append(j)
#     return sueldo_ingreso[0]  

@st.cache_data
def ingreso_mensual(df, filtro):
    '''Funcion filtra el ingreso mensual por estado'''
    df = df.dropna(subset = ['Sueldo'])
    if filtro in df['Estado'].unique() :
        sueldo_ingreso = []
        for i, j in zip(df['Estado'], df['Ingreso_mensual']):
            if i == filtro:
                sueldo_ingreso.append(j)

    else:
        sueldo_ingreso= []
        sueldo_ingreso.append(0)

    return sueldo_ingreso[0]

# ----------------- MAPA -------------------
def display_map(df):
    '''Funcion empleada para visualizar la distribución geográfica de las ofertas laborales'''
    # Agrupar y resetar el índice para que 'Estado' sea una columna
    # df = df.groupby(['Estado', 'Ingreso_mensual'])['Estado'].size().reset_index(name='Conteo') #agrupamos las columanas y hacemos un subset del estado
    
    df = df.groupby(['Estado','Sueldo', 'Ingreso_mensual'])['Estado'].count().reset_index(name='Conteo')
    df = df.groupby('Estado').agg(conteo = ('Conteo', 'sum') , sueldo_minimo = ('Sueldo', 'min'), sueldo_maximo = ('Sueldo', 'max'),
                                                            ENSAFI = ('Ingreso_mensual','first')).reset_index()

        
    # Unir el conteo al GeoDataFrame
    gdf = gpd.read_file('data/georef-mexico-state@public2.geojson')
    gdf = gdf.merge(df, left_on='sta_name', right_on='Estado', how='left')
    # st.write(df)
    
    # Verificar que hay datos
    if df.empty:
        st.warning("No hay datos para mostrar el mapa.")
        return
    
    map = folium.Map(location=[23.6345, -102.5528], zoom_start=5, scrollWheelZoom=False, tiles="cartodb positron")
    # st.dataframe(df)
    choropleth = folium.Choropleth(
        geo_data= gdf,
        name="Ofertas",
        data= gdf,
        columns=['Estado', 'conteo', 'sueldo_minimo', 'sueldo_maximo', 'ENSAFI'],  # Usar Estado y la columna de conteo
        key_on='feature.properties.sta_name', # el partado donde esta el nombre de los estados en el archivo json
        # binds= 2,
        fill_color="YlGn",
        nan_fill_color="black",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name="Número de ofertas",
        smooth_factor=0,
        highlight=True,
        line_color='black'
    )
    
    choropleth.add_to(map)
    
    # https://python-visualization.github.io/folium/latest/user_guide/geojson/geojson_popup_and_tooltip.html
    choropleth.geojson.add_child(
        folium.features.GeoJsonTooltip(
            fields=["sta_name", 'conteo', 'sueldo_minimo', 'sueldo_maximo', 'ENSAFI'],
            aliases=["Estado: ", "Ofertas: ",'Sueldo mínimo: ', 'Sueldo máximo: ' , "ENSAFI,(2024): "],
            localize=True,
            sticky=False,
            labels=True,
            # style='''
            #     background-color: #F0EFEF;
            #     border: 2px solid black;
            #     border-radius: 3px;
            #     box-shadow: 3px;
            #     ''',
            #     max_width=800
            ))
    
    # https://discuss.streamlit.io/t/caching-folium-maps-with-new-st-experimental-memo/33557
    # https://discuss.streamlit.io/t/how-to-avoid-page-reload-on-interaction/40735/3
    return st_folium(map, width=700, height=450,  key="map", use_container_width=True, returned_objects=[])
    # st_map = st_folium(map, width=700, height=450) #Tamaño optimo para celulas de 6.5"
    
# ----------------- Gráficos -------------------  
def grafico_barras(df, filtro):
    '''Funcion genera grafico de barras para las 5 palabras más comunes'''
    palabras = []
    lista_palabras = ['empresa','experiencia','descripción','prácticas','sector','buenas','Medical','clientes','clientes/as']
    
    if filtro:
        df = df[df['Relación_profesional'] == filtro]
        for i in df['Toda'].dropna():
            palabra = i.replace(u',', u'').replace(u':', u'').replace(u'!', u'').strip().split(' ') # con split(' ') es para seperar por palabras
            for j in palabra:
                if len(j) >=6 and j.lower() not in lista_palabras:
                    palabras.append(j.lower())

    fdist = nltk.FreqDist(palabras) 

    numero_palabra = []
    frecuencia = []

    for i in fdist.most_common(5): #palabras mas comunes
        numero_palabra.append(i[0])
        frecuencia.append(i[1])

    diccionario = {'Palabra':numero_palabra, 'Frecuencia':frecuencia}
    tabla = pd.DataFrame(diccionario) 

    # titulo = 'Laboratorio'
    fig = px.bar(tabla, x='Palabra', y='Frecuencia',color='Palabra', title= f'Top 5 de palabras más frecuentes para {filtro}',
            #  labels={'Palabra':'Frecuencia de palabras', 'Frecuencia':'Número'},
            height=400)
    
    fig.update_layout(showlegend=False)
    fig.update_layout(
    title={
        'x': 0.5,
        'xanchor': 'center'
        }
    )
    # https://docs.streamlit.io/develop/api-reference/charts/st.plotly_chart
    return st.plotly_chart(fig, use_container_width=True)

### funcion con n-gram
# def grafico_barras_2(df, filtro):
#     '''Funcion para crear grafico con palabras mas frecuentes usando freq.plot de nltk'''

#     lista_palabras = ['empresa','experiencia','descripción','prácticas','sector','buenas','Medical','clientes','clientes/as']

#     trigram = []

#     if filtro:
#         df = df[df['Relación_profesional'] == filtro]
#         for i in df['Toda'].dropna():
#             token = i.lower().replace(u',', u'').strip().split(' ')
#             # if len(token) >=6 and token not in lista_palabras:
#             trigram.extend(nltk.ngrams(token, 3))

#     freq = nltk.FreqDist(trigram)

#     palabra = []
#     frecuencia = []

#     for f in freq.most_common(5): #palabras mas comunes
#         palabra.append(f[0])
#         frecuencia.append(f[1])

#     palabras = []
#     for word in palabra:
#         palabras.append(' '.join(word))


#     diccionario = {'Palabra':palabras, 'Frecuencia':frecuencia}
#     tabla = pd.DataFrame(diccionario)
#     fig = px.bar(tabla, x='Palabra', y='Frecuencia',color='Palabra', title= f'Frecuencia de palabras para {filtro}',
#                     #  labels={'Palabra':'Frecuencia de palabras', 'Frecuencia':'Número'},
#                     height=400)

#     fig.update_layout(showlegend=False)
#     fig.update_layout(
#     title={
#         'x': 0.5,
#         'xanchor': 'center'
#         }
#     )

#     return st.plotly_chart(fig)

### Graficode clusters
def cluster_sueldo(df):
    '''Agrupamiento de palabras con sueldos'''
    selected_data = df[['Frecuencia', 'Sueldo']].copy()

    model = cluster.KMeans(n_clusters = 3, init = 'k-means++')
    kmeans = model.fit(selected_data)

    df['Grupo'] = (kmeans.labels_ + 1).astype(str)

    fig = px.scatter(df, x='Sueldo', y='Frecuencia', color='Grupo',
                    hover_data= 'Palabra',
                    # color_discrete_sequence=["red", "green", "blue", "orange", "mediumpurple"],
                    color_discrete_sequence=px.colors.qualitative.G10,
                    category_orders={"Grupo": ["1", "2", "3", "4", "5"]},
                    title="Sueldos y palabras claves")
    fig.update_layout(
    title={
        'x': 0.5,
        'xanchor': 'center'
        }
    )

    return st.plotly_chart(fig, use_container_width=True)

##Sueldo a predecir funciona siempre y cuando exista una relacion lineal
# def sueldo_predict(df, actividad_1, actividad_2, actividad_3):
#     '''Funcion predice apartir de regresion lineal los sueldo '''
#     # lista_palabras = [''] + list(df['Palabra'].unique())
#     # lista_palabras.sort()
#     # palabra = st.sidebar.selectbox('Actividad', lista_palabras)
    
#     #palabras de eleccion
#     eleccion_1 = df[df['Palabra'] == actividad_1]
#     eleccion_2 = df[df['Palabra'] == actividad_2]
#     eleccion_3 = df[df['Palabra'] == actividad_3]

#     X = df[['Frecuencia']].values ## de esta forma se hacen los arreglos
#     y = df[['Sueldo']].values

#     #Select lineal model
#     model = LinearRegression()
#     #train the model
#     model.fit(X, y)

#     #make a prediction
#     x_new_1 = [eleccion_1['Frecuencia']] ## Esto debe de ir como arreglo
#     x_new_2 = [eleccion_2['Frecuencia']]
#     x_new_3 = [eleccion_3['Frecuencia']]

#     # Calculate the average prediction.
#     average_prediction = (model.predict(x_new_1) + model.predict(x_new_2) + model.predict(x_new_3)) / 3

#     #https://stackoverflow.com/questions/1995615/how-can-i-format-a-decimal-to-always-show-2-decimal-places
#     st.write(f'El promedio de tu sueldo sería: ${average_prediction[0][0]:.2f}')  ## Prediccion del sueldo

#valores negativo rojo en el dataframe
# def highlight_positive_negative(value):
#     if isinstance(value, (int, float)):
#         if value < 0:
#             color = 'lightcoral'  # Red for negative
#         elif value > 0:
#             color = ''  # Green for positive
#         else:
#             color = ''  # Default for zero
#         return f'background-color: {color};'
#     return ''

# ----------------- Discrepancias-----------
def sueldo_discrepancias(df):
    '''Funcion que grafica las discrepancias entre sueldos e ingreso necesario'''
    import plotly.graph_objects as px
    df = df.groupby('Estado')[['Sueldo', 'Ingreso_mensual']] \
                            .mean().round(2).dropna().reset_index()
    #Grafico de disrepancia
    fig = px.Figure(data=[px.Bar(
    name = 'Sueldo promedio',
    marker_color='#25d172',
    x = df['Estado'],
    y = df['Sueldo']
    ),
                       px.Bar(
    name = 'Ingreso básico necesario',
    marker_color = '#fc0e03',
    x = df['Estado'],
    y = df['Ingreso_mensual']
    )
    ])

    # fig.update_layout(font_family="serif",  font=dict(size=14))
    # plot.update_layout(
    # title=dict(text="Sueldo vs ingreso minimo", font=dict(size=50), automargin=True, yref='paper'))
    fig.update_layout(
    title={
        'text': "Sueldo vs ingreso básico necesario",
        'x':0.5,
        'xanchor': 'center'})
    
    fig.update_layout(legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1
    ))

    return st.plotly_chart(fig, use_container_width=True)

# ----------------- Preddicion con Random Forest regression -----------
def prediccion_rfr(df):
    '''Funcion predice el sueldo mediante Random Forest regression a partir del estado y la relacion profesional'''
    #modelo
    # model = joblib.load('./model_RandomForestRegressor.pkl')
    
    #Dataframe extraccion
    df = df[['Nombre','Estado','id_estado','Relación_profesional','id_relaciones','Sueldo']] \
                                                    .dropna(subset=['Sueldo']).reset_index(drop=True)
    col1, col2 = st.columns(2)
    with col1:
    #Lista de estados
        lista_estados = [''] + list(df['Estado'].unique())
        lista_estados.sort()
        estado_id =  st.selectbox(':flag-mx: Estado', lista_estados )
        
    with col2:
    #lista de relaciones profesionales
        lista_relaciones = [''] + list(df['Relación_profesional'].unique())
        lista_relaciones.sort()
        relacion_id = st.selectbox(':round_pushpin: Relación profesional', lista_relaciones)

    ## id's de los estados y relaciones
    # if estado_id == '' and relacion_id == '':
    #     estado_oferta = 0
    #     relacion_oferta = 0
        
    #     X = [[int(estado_oferta) , int(relacion_oferta)]]
    #     X_array = np.array(X)
    
    # Inicializar valores
    X_array = None   
    
    if estado_id != '' and relacion_id != '':    
        estado_oferta = [df[df['Estado'] == estado_id]['id_estado'].unique()][0]
        relacion_oferta = [df[df['Relación_profesional']== relacion_id]['id_relaciones'].unique()][0]
        
        X = [[int(estado_oferta) , int(relacion_oferta)]]
        X_array = np.array(X)
    
    # ##Predicción de sueldo 
    # prediction = model.predict(X_array)
    else:
        st.warning("Por favor selecciona *Estado* y *Campo profesional* para realizar la predicción.")

    return  estado_id, relacion_id, X_array


# ----------------- MAIN -------------------
def main():
    '''Funcion principal de la applicacion'''
    #-------- configuracion de pagina ------------
    ### edicion del tamaño del titulo
    # original_title = '<p style="font-family:Courier; color:Blue; font-size: 20px;">Ofertas laborales en México</p>'
    # st.markdown(original_title, unsafe_allow_html=True)
    
    st.set_page_config(page_title="Ofertas Laborales", 
                     page_icon="📊", 
                     layout="wide",
                     initial_sidebar_state="collapsed",
                     menu_items=None)
    
    st.title(APP_TITLE)
    st.caption(APP_SUB_TITLE)
    
    # st.sidebar.title(":red-background[INFORMACION]\nV.1.0")
    #link de Contacto
    url = "https://github.com/Br1Rdz/"
    
    markdown = """
    Developed by Bruno Rodriguez
    """
    #-------- Hide streamlit style ------------    
    hide_st_style = '''
                    <style>
                    #Main Menu {visibility:hidden;}
                    footer {visibility:hidden;}
                    header {visibility:hidden;}
                    </style>
    '''
    st.markdown(hide_st_style, unsafe_allow_html= True)
    
    #--------- Carga de datos ------------------
    # df_ofertas_laborales = pd.read_csv('./Ofertas_juntas.csv') # hay que quitar los outlier
    # soluccion de error de path
    # https://discuss.streamlit.io/t/no-such-file-or-directory-error/38338/3
    df_ofertas_ids = pd.read_csv('data/Tabla_ids.csv') ## con ids de estado y ids relaciones
    df_ofertas_laborales = pd.read_csv('data/Tabla_ofertas.csv') 
    df_cluster = pd.read_csv('data/Tabla_cluster.csv') ## Tabla para los grupos por frecuencia y sueldo
    # df_ingreso_mensual = pd.read_csv('./Tablas_entrada/df_filtrada.csv') ## sin NA en los sueldos
    
    #Eleccion de palabras para usuario
    # lista_palabras = [''] + list(df_limpia['Palabra'].unique())
    # lista_palabras.sort()
    # lista_top = [''] + ['experiencia', 'químico','calidad', 'empresa', 'farmacéutico',
    #                     'biólogo', 'equipo', 'productos','trabajo','gestión']

    # palabra_1= st.sidebar.selectbox('Actividad 1', lista_top)
    # palabra_2= st.sidebar.selectbox('Actividad 2', lista_top)
    # palabra_3= st.sidebar.selectbox('Actividad 3', lista_top)
    
    #Filtro y mapa
    df_filtrada, Campo_laboral = base_filtrada(df_ofertas_laborales)
    
    # distribucion_ofertas = display_map(df_filtrada)
    sueldo_minimo, estado_minimo, estado_maximo, sueldo_maximo = sueldo_min_max_estado(df_filtrada)
    
    # tipar variables https://cosasdedevs.com/posts/tipado-python/
    ingreso_minimo:int = ingreso_mensual(df_filtrada, estado_minimo)# Hay que tener cuidado con las columnas de sueldo e ingreso
    ingreso_maximo:int = ingreso_mensual(df_filtrada, estado_maximo)# porque libreoffice cal puede ponerlas como text
    
    sueldo_ingreso_minimo:int = round(sueldo_minimo - ingreso_minimo)
    sueldo_ingreso_maximo:int = round(sueldo_maximo - ingreso_maximo)
    
    #Esto es para la prediccion de sueldo apartir de tus habilidades
    # lista_top = [''] + ['experiencia', 'químico','calidad', 'empresa', 'farmacéutico',
    #                     'biólogo', 'equipo', 'productos','trabajo','gestión']

    # palabra_1= st.sidebar.selectbox('Actividad 1', lista_top)
    # palabra_2= st.sidebar.selectbox('Actividad 2', lista_top)
    # palabra_3= st.sidebar.selectbox('Actividad 3', lista_top)
    
    ##prediccion con Random Forest regression
    # estado_id, relacion_id, X_array = prediccion_rfr(df_ofertas_ids)
    
    ## variable de uso de app
    # explicacion = '''Esta aplicación utiliza información recopilada de ofertas laborales para biólogos 
    # y biólogas publicadas en los portales OCC y Computrabajo. En esta primera sección se presenta:
    # La distribución geográfica de todas las ofertas laborales.
    # Los grupos de palabras clave asociados y los sueldos correspondientes.
    # La discrepancia entre el sueldo promedio ofrecido por entidad federativa y 
    # el ingreso mensual necesario estimado por la ENSAFI (2024).
    # Según la Encuesta Nacional sobre Finanzas Individuales (ENSAFI, 2024),
    # en promedio, una persona en México necesita $16,421 pesos mensuales para cubrir sus gastos básicos.
    # Este monto puede variar según la región, el tamaño del hogar y el estilo de vida.
    # Los gastos básicos considerados incluyen alimentación, vivienda, servicios, transporte, educación y vestimenta.
    # Desde la barra lateral, selecciona la opción "Relación profesional" 
    # para explorar las distintas categorías de las ofertas laborales.'''
    
    # ENSAFI = ''' En promedio, un mexicano necesita un ingreso mensual de $16,421 para cubrir sus gastos básicos,
    #              según la Encuesta Nacional sobre Finanzas Individuales (ENSAFI, 2024).
    #              El ingreso necesario para cubrir gastos básicos puede variar dependiendo de la región,
    #              el tamaño del hogar y el estilo de vida. Los gastos básicos que pueden incluirse en el presupuesto son:
    #              Comida, vivienda, servicios, transporte, educación y vestimenta.'''

    ## Explicacion de la app en sidebar con botton
    # with st.sidebar.info(''):
    #         if st.button('Uso de app'):
    #             st.write(response_generator(explicacion)) 
                
    ## configuracion de app            
    # st.sidebar.info(markdown)
    # st.sidebar.info("Github: [Br1Rdz](%s)" % url)

    # logo = "./Clicker.png"
    # st.sidebar.image(logo) 
    st.logo("./Informacion.png", icon_image="./info2.png")
    
    ##Tabla sin sueldos NaN
    valores = df_ofertas_laborales['Sueldo'].dropna()
    
    #modelo de Random Forest regression
    model = joblib.load('data/model_RandomForestRegressor_Mayo_sin_outlier.pkl')
    
    #todas las ofertas laborales
    if Campo_laboral == '':
        
        # #Explicacion de la app
        # with st.expander(':bangbang: Uso de la app'):
        #     if st.button("présioname"):
        #         st.write(response_generator(explicacion)) 

        #Este ejemplo es con markdown
        # with st.expander('# Uso de la app:'):
            # https://discuss.streamlit.io/t/how-do-i-align-st-title/1668/7
            # st.markdown(
            #     "<h6 style='text-align: justify;'>Esta aplicación utiliza información recopilada de ofertas laborales \
            #     para biólogx de los portales OCC y Computrabajo. \
            #     Selecciona de la barra lateral la 'Relación profesional' para comenzar.</h6>", unsafe_allow_html=True)
            
        # st.markdown(f"<style> \
        #             .subheader {{ font-size: 24px; font-weight: bold; }} \
        #             </style>", unsafe_allow_html=True)   
        
        st.header(f':clipboard: {len(df_ofertas_laborales)} ofertas laborales para biólogo', divider="gray")
        col1, col2 = st.columns(2)
        ## edicion del tamaño de letra
        # st.markdown(
        #                 """
        #             <style>
        #             [data-testid="stMetricValue"] {
        #                 font-size: 12px;
        #             }
        #             </style>
        #             """,
        #                 unsafe_allow_html=True,
        #             )
        with col1:
            st.metric(label= f'Sueldo mínimo mensual', 
                      value= f'${round(min(valores)):,}')
        with col2:
            st.metric(label= f'Sueldo máximo mensual', 
                      value= f'${round(max(valores)):,}')
            
        # https://discuss.streamlit.io/t/changing-width-of-a-metric-card-using-css/69905
        style_metric_cards(border_left_color="#999999",
                           background_color='#00000',
                           border_color="#999999",
                           border_radius_px=20)#esto quita los bordes
        
        with st.expander(':chart_with_upwards_trend: Grupos de sueldos y palabras claves'):
            # https://discuss.streamlit.io/t/how-do-i-align-st-title/1668/7
            st.markdown(
                "<h6 style='text-align: justify;'>Se muestran los grupos formados a partir de las palabras clave \
                y los sueldos de todas las ofertas laborales.</h6>", unsafe_allow_html=True)    
            #graficos de cluster
            cluster_sueldo(df_cluster)
            
        with st.expander(':bar_chart: Discrepancia entre sueldos e ingreso mínimo necesario'):
            # https://discuss.streamlit.io/t/how-do-i-align-st-title/1668/7
            st.markdown(
                "<h6 style='text-align: justify;'>Se muestran las diferencias entre el promedio de las ofertas de los \
                sueldos por entidad federativa y el ingreso mínimo necesario \
                </h6>", unsafe_allow_html=True)     
            #grafico de discrepancia
            sueldo_discrepancias(df_ofertas_laborales)
        
        with st.expander(':sparkles: Predicción de sueldo'):
            # Random Forest Regression
            st.markdown(
                "<h6 style='text-align: justify;'>La predicción del sueldo se realiza considerando \
                la ubicación geográfica y su relación profesional. \
                </h6>", unsafe_allow_html=True)
            
            estado_id, relacion_id, X_array = prediccion_rfr(df_ofertas_ids)
            
            prediccion_button = st.button('présioname para predecir')   
            if prediccion_button:
                prediction = model.predict(X_array)
                st.write(f'El sueldo para {relacion_id} en {estado_id} seria ${prediction[0]:,.2f}')
                # st.balloons()
        
    #Filtro de las ofertas laborales
    if Campo_laboral != '':
        # # dialogo de explicacion sobre ENSAFI
        # with st.expander('Que es el ingreso mensual necesario (ENSAFI,2024)'):
        #     if st.button("Explicacion"):
        #         st.write(response_generator(ENSAFI)) 
        
        #con markdown        
        # st.markdown("<h6 style='text-align: justify;'>Ingreso necesario para cubrir gastos básicos\
        #         (Encuesta Nacional sobre Finanzas Individuales, 2024).</h6>", unsafe_allow_html=True)
        
        columna1, columna2 = st.columns(2)
        ## edicion del tamaño de letra
        # st.markdown(
        #                 """
        #             <style>
        #             [data-testid="stMetricValue"] {
        #                 font-size: 12px;
        #             }
        #             </style>
        #             """,
        #                 unsafe_allow_html=True,
        #             )
        
        with columna1:
            st.write(f'Ingreso en {estado_minimo} es ${round(ingreso_minimo):,} (ENSAFI, 2024)')
        with columna2:
            st.write(f'Ingreso en {estado_maximo} es ${round(ingreso_maximo):,} (ENSAFI, 2024)')
                
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label= f'Sueldo oferta mínimo mensual en {estado_minimo}', 
                      value= '${:,}'.format(round(sueldo_minimo)),
                      delta = f'{sueldo_ingreso_minimo:,}', delta_color="normal")
        with col2:
            st.metric(label= f'Sueldo oferta máximo mensual en {estado_maximo}', 
                      value= '${:,}'.format(round(sueldo_maximo)),
                      delta = f'{sueldo_ingreso_maximo:,}', delta_color="normal")
                    #   delta = '-${:,}'.format(round((sueldo_maximo - sueldo_minimo))))
                    
        style_metric_cards(border_left_color="#999999",
                           background_color='#00000',
                           border_color="#999999",
                           border_radius_px=20)#esto quita los bordes    
    # st.balloons()
    with st.spinner(':robot_face: Espera mientras elaboró el mapa...'):  
        display_map(df_filtrada)
    #si hubiera una relacion lineal    
    # if palabra_1 and palabra_2 and palabra_3:
    #     sueldo_predict(df_limpia, palabra_1, palabra_2, palabra_3)
       
        # st.success('Gracias por esperar...') 
    if Campo_laboral != '':
        grafico_barras(df_filtrada, Campo_laboral)
        # cluster_sueldo(df_cluster)
            
        with st.expander("Trabajo por Estado", icon="🔥", expanded=False): 
            
            st.markdown("<h6 style='text-align: center;'>Ofertas laborales por localidad</h6>", unsafe_allow_html=True) 
            
            df_filled = dataframe_explorer(df_filtrada[['Nombre', 'Ciudad', 'Estado', 'Sueldo', 'Ingreso_mensual','Diferencia']].fillna('No disponible')) ## sale un warning
            # styled_df = df_filled.style.applymap(highlight_positive_negative)
            st.dataframe(df_filled,
                            column_order=('Nombre', 'Ciudad', 'Sueldo', 'Ingreso_mensual','Diferencia'), ## Hay que agragar la de ingreso_mensual
                            hide_index = True,
                            width = 800,
                            height = 200,
                            column_config={
                            "Nombre":st.column_config.TextColumn(
                                "Puesto",
                                help="Nombre del puesto"
                                # width="none",
                                # required=True
                                ),
                            "Ciudad":st.column_config.TextColumn(
                                "Localidad",
                                help="Ubicación del puesto"
                                # width="none",
                                # required=True
                                ),
                            "Sueldo":st.column_config.NumberColumn(
                                "Sueldo (mensual)",
                                help="Sueldo del puesto",
                                format="$%d"
                                # width="none",
                                # required=True
                                # min_value=0,
                                # max_value=max(df_filtrada.Sueldo),
                            ),
                            "Ingreso_mensual":st.column_config.NumberColumn(
                                "Ingreso (ENSAFI,2024)",
                                help="Ingreso mínimo necesario",
                                format="$%d"
                                # width="none",
                                # required=True
                                # min_value=0,
                                # max_value=max(df_filtrada.Ingreso_mensual),
                            ),
                            "Diferencia":st.column_config.NumberColumn(
                            "Discrepancia",
                            help="Discrepancia entre sueldo e ingreso mínimo necesario",
                            format="$%d")
                            },
                            use_container_width = True
                        )   
                    

if __name__ == '__main__':
    main()