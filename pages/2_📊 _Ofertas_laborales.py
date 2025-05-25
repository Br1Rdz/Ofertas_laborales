import streamlit as st 
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.dataframe_explorer import dataframe_explorer
import pandas as pd
import geopandas as gpd
import numpy as np
import folium
from streamlit_folium import st_folium
import time
import nltk
import plotly.express as px
from sklearn.cluster import KMeans
import sklearn.cluster as cluster
import joblib

APP_TITLE = 'Ofertas laborales en México'
APP_SUB_TITLE = ':briefcase: Fuente de OCC y Computrabajo'

# ----------------- Uso de app -------------------
# def response_generator(texto):
#     '''Esta funcion es para mostrar texto letra por letra con un retraso'''
#     for letra in texto.split():
#         yield letra + " "
#         time.sleep(0.1)  

# ----------------- FILTRADO -------------------
def base_filtrada(df):
    '''Esta funcion realiza filtros a la base de datos a partir de los requerimentos del usuario'''
       
    lista_laboral = [''] + list(df['Relación_profesional'].unique())
    lista_laboral.sort()
    Campo_laboral = st.sidebar.selectbox(':round_pushpin: Relación profesional', lista_laboral)
        
    if Campo_laboral:
        df = df[df['Relación_profesional'] == Campo_laboral]      
    
    #numero de filas con coencidencia
    numero = len(df)
    
    if Campo_laboral:
        st.subheader(f':clipboard: {numero} ofertas laborales para {Campo_laboral}', divider="gray")

    return df, Campo_laboral 

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
        columns=['Estado', 'conteo', 'sueldo_minimo', 'sueldo_maximo', 'ENSAFI'],  
        key_on='feature.properties.sta_name', 
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
    
    choropleth.geojson.add_child(
        folium.features.GeoJsonTooltip(
            fields=["sta_name", 'conteo', 'sueldo_minimo', 'sueldo_maximo', 'ENSAFI'],
            aliases=["Estado: ", "Ofertas: ",'Sueldo mínimo: ', 'Sueldo máximo: ' , "ENSAFI,(2024): "],
            localize=True,
            sticky=False,
            labels=True
            ))
    
    return st_folium(map, width=700, height=450,  key="map", use_container_width=True, returned_objects=[])
    
# ----------------- Gráficos -------------------  
def grafico_barras(df, filtro):
    '''Funcion genera grafico de barras para las 5 palabras más comunes'''
    palabras = []
    lista_palabras = ['empresa','experiencia','descripción','prácticas','sector','buenas','Medical','clientes','clientes/as']
    
    if filtro:
        df = df[df['Relación_profesional'] == filtro]
        for i in df['Toda'].dropna():
            palabra = i.replace(u',', u'').replace(u':', u'').replace(u'!', u'').strip().split(' ') 
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

    fig = px.bar(tabla, x='Palabra', y='Frecuencia',color='Palabra', title= f'Top 5 de palabras más frecuentes para {filtro}',
            height=400)
    
    fig.update_layout(showlegend=False)
    fig.update_layout(
    title={
        'x': 0.5,
        'xanchor': 'center'
        }
    )
    return st.plotly_chart(fig, use_container_width=True)

### Graficode clusters
def cluster_sueldo(df):
    '''Agrupamiento de palabras con sueldos'''
    selected_data = df[['Frecuencia', 'Sueldo']].copy()

    model = cluster.KMeans(n_clusters = 3, init = 'k-means++')
    kmeans = model.fit(selected_data)

    df['Grupo'] = (kmeans.labels_ + 1).astype(str)

    fig = px.scatter(df, x='Sueldo', y='Frecuencia', color='Grupo',
                    hover_data= 'Palabra',
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
    
    # Inicializar valores
    X_array = None   
    
    if estado_id != '' and relacion_id != '':    
        estado_oferta = [df[df['Estado'] == estado_id]['id_estado'].unique()][0]
        relacion_oferta = [df[df['Relación_profesional']== relacion_id]['id_relaciones'].unique()][0]
        
        X = [[int(estado_oferta) , int(relacion_oferta)]]
        X_array = np.array(X)
    
    # ##Predicción de sueldo 
    else:
        st.warning("Por favor selecciona *Estado* y *Campo profesional* para realizar la predicción.")

    return  estado_id, relacion_id, X_array


# ----------------- MAIN -------------------
def main():
    '''Funcion principal de la applicacion'''
    #-------- configuracion de pagina -----------    
    st.set_page_config(page_title="Ofertas Laborales", 
                     page_icon="📊", 
                     layout="wide",
                     initial_sidebar_state="collapsed",
                     menu_items=None)
    
    st.title(APP_TITLE)
    st.caption(APP_SUB_TITLE)
    
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
    df_ofertas_ids = pd.read_csv('data/Tabla_ids.csv') ## con ids de estado y ids relaciones
    df_ofertas_laborales = pd.read_csv('data/Tabla_ofertas.csv') 
    df_cluster = pd.read_csv('data/Tabla_cluster.csv') ## Tabla para los grupos por frecuencia y sueldo
   
    #Filtro y mapa
    df_filtrada, Campo_laboral = base_filtrada(df_ofertas_laborales)
    
    # distribucion_ofertas = display_map(df_filtrada)
    sueldo_minimo, estado_minimo, estado_maximo, sueldo_maximo = sueldo_min_max_estado(df_filtrada)
    
    ingreso_minimo:int = ingreso_mensual(df_filtrada, estado_minimo)
    ingreso_maximo:int = ingreso_mensual(df_filtrada, estado_maximo)
    
    sueldo_ingreso_minimo:int = round(sueldo_minimo - ingreso_minimo)
    sueldo_ingreso_maximo:int = round(sueldo_maximo - ingreso_maximo)
    
    st.logo("./Informacion.png", icon_image="./info2.png")
    
    ##Tabla sin sueldos NaN
    valores = df_ofertas_laborales['Sueldo'].dropna()
    
    #modelo de Random Forest regression
    model = joblib.load('data/model_RandomForestRegressor_Mayo_sin_outlier.pkl')
    
    #todas las ofertas laborales
    if Campo_laboral == '':
        
        st.header(f':clipboard: {len(df_ofertas_laborales)} ofertas laborales para biólogo', divider="gray")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(label= f'Sueldo mínimo mensual', 
                      value= f'${round(min(valores)):,}')
        with col2:
            st.metric(label= f'Sueldo máximo mensual', 
                      value= f'${round(max(valores)):,}')
            
        style_metric_cards(border_left_color="#999999",
                           background_color='#00000',
                           border_color="#999999",
                           border_radius_px=20)#esto quita los bordes
        
        with st.expander(':chart_with_upwards_trend: Grupos de sueldos y palabras claves'):
            st.markdown(
                "<h6 style='text-align: justify;'>Se muestran los grupos formados a partir de las palabras clave \
                y los sueldos de todas las ofertas laborales.</h6>", unsafe_allow_html=True)    
            #graficos de cluster
            cluster_sueldo(df_cluster)
            
        with st.expander(':bar_chart: Discrepancia entre sueldos e ingreso mínimo necesario'):
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
                st.audio('data/Finish.mp3', autoplay=True)
                
    #Filtro de las ofertas laborales
    if Campo_laboral != '':
        
        columna1, columna2 = st.columns(2)
        
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
                    
        style_metric_cards(border_left_color="#999999",
                           background_color='#00000',
                           border_color="#999999",
                           border_radius_px=20)#esto quita los bordes    
    with st.spinner(':robot_face: Espera mientras elaboró el mapa...'):  
        display_map(df_filtrada)
     
    if Campo_laboral != '':
        grafico_barras(df_filtrada, Campo_laboral)
            
        with st.expander("Trabajo por Estado", icon="🔥", expanded=False): 
            
            st.markdown("<h6 style='text-align: center;'>Ofertas laborales por localidad</h6>", unsafe_allow_html=True) 
            
            df_filled = dataframe_explorer(df_filtrada[['Nombre', 'Ciudad', 'Estado', 'Sueldo', 'Ingreso_mensual','Diferencia']].fillna('No disponible')) ## sale un warning
            st.dataframe(df_filled,
                            column_order=('Nombre', 'Ciudad', 'Sueldo', 'Ingreso_mensual','Diferencia'), 
                            hide_index = True,
                            width = 800,
                            height = 200,
                            column_config={
                            "Nombre":st.column_config.TextColumn(
                                "Puesto",
                                help="Nombre del puesto"
                          
                                ),
                            "Ciudad":st.column_config.TextColumn(
                                "Localidad",
                                help="Ubicación del puesto"
                           
                                ),
                            "Sueldo":st.column_config.NumberColumn(
                                "Sueldo (mensual)",
                                help="Sueldo del puesto",
                                format="$%d"
                              
                            ),
                            "Ingreso_mensual":st.column_config.NumberColumn(
                                "Ingreso (ENSAFI,2024)",
                                help="Ingreso mínimo necesario",
                                format="$%d"
                         
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
