import streamlit as st 
import pandas as pd
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
from sklearn.linear_model import LinearRegression


APP_TITLE = 'Ofertas laborales en México'
APP_SUB_TITLE = 'Fuente de OCC y Computrabajo'

# ----------------- Uso de app -------------------
# https://docs.streamlit.io/develop/api-reference/write-magic/st.write_stream
def response_generator(texto):
    '''Esta funcion es para mostrar texto letra por letra con un retraso'''
    for letra in texto.split():
        yield letra + " "
        time.sleep(0.05)  

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
    Campo_laboral = st.sidebar.selectbox('Relación profesional', lista_laboral)
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
        st.subheader(f'{numero} ofertas laborales para {Campo_laboral}', divider="gray")

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
    df = df.groupby('Estado').size().reset_index(name='Conteo')
    # st.write(df)
    
    # Verificar que hay datos
    if df.empty:
        st.warning("No hay datos para mostrar el mapa.")
        return
    
    map = folium.Map(location=[23.6345, -102.5528], zoom_start=4.2, scrollWheelZoom=False, tiles="cartodb positron")
    
    choropleth = folium.Choropleth(
        geo_data='./georef-mexico-state@public2.geojson',
        name="Ofertas",
        data=df,
        columns=['Estado', 'Conteo'],  # Usar Estado y la columna de conteo
        key_on='feature.properties.sta_name', # el partado donde esta el nombre de los estados en el archivo json
        binds= 2,
        fill_color="YlGn",
        nan_fill_color="black",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name="Número de ofertas",
        smooth_factor=0,
        highlight=True
    )
    
    choropleth.add_to(map)
    
    # https://python-visualization.github.io/folium/latest/user_guide/geojson/geojson_popup_and_tooltip.html
    choropleth.geojson.add_child(
        folium.features.GeoJsonTooltip(
            fields=["sta_name"],
            # aliases=["Estado:"],
            # localize=True,
            # sticky=False,
            labels=False
            # style="""
            # background-color: #F0EFEF;
            # border: 2px solid black;
            # border-radius: 3px;
            # box-shadow: 3px;
            # """,
            # max_width=800
            ))
    # https://discuss.streamlit.io/t/caching-folium-maps-with-new-st-experimental-memo/33557
    st_map = st_folium(map, width=350, height=350,  key="map", use_container_width=True, returned_objects=["last_object_clicked"])
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

    model = cluster.KMeans(n_clusters=4, init='k-means++')
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

# ----------------- MAIN -------------------
def main():
    '''Funcion principal de la applicacion'''
    #-------- configuracion de pagina ------------
    ### edicion del tamaño del titulo
    # original_title = '<p style="font-family:Courier; color:Blue; font-size: 20px;">Ofertas laborales en México</p>'
    # st.markdown(original_title, unsafe_allow_html=True)
    
    # st.set_page_config(APP_TITLE)
    st.title(APP_TITLE)
    st.caption(APP_SUB_TITLE)
    
    # st.sidebar.title(":red-background[INFORMACION]\nV.1.0")
    st.sidebar.title("INFORMACION\nV.1.0")
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
    df_ofertas_laborales = pd.read_csv('./Tablas_entrada/Tabla_concatenada.csv') # hay que quitar los outlier
    df_cluster = pd.read_csv('./Tablas_entrada/Tabla_cluster.csv') ## Tabla para los grupos por frecuencia y sueldo
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
    
    sueldo_ingreso_minimo:int = round(ingreso_minimo - sueldo_minimo)
    sueldo_ingreso_maximo:int = round(sueldo_maximo - ingreso_maximo)
    
    #Esto es para la prediccion de sueldo apartir de tus habilidades
    # lista_top = [''] + ['experiencia', 'químico','calidad', 'empresa', 'farmacéutico',
    #                     'biólogo', 'equipo', 'productos','trabajo','gestión']

    # palabra_1= st.sidebar.selectbox('Actividad 1', lista_top)
    # palabra_2= st.sidebar.selectbox('Actividad 2', lista_top)
    # palabra_3= st.sidebar.selectbox('Actividad 3', lista_top)
    
    ## variable de uso de app
    explicacion = '''Esta aplicación utiliza información recopilada de ofertas laborales 
                   para biólogx de los portales OCC y Computrabajo. 
                   Selecciona de la barra lateral la 'Relación profesional' para comenzar.'''
    
    ENSAFI = ''' En promedio, un mexicano necesita un ingreso mensual de $16,421 para cubrir sus gastos básicos,
                 según la Encuesta Nacional sobre Finanzas Individuales (ENSAFI, 2024).
                 El ingreso necesario para cubrir gastos básicos puede variar dependiendo de la región,
                 el tamaño del hogar y el estilo de vida. Los gastos básicos que pueden incluirse en el presupuesto son:
                 Comida, vivienda, servicios, transporte, educación y vestimenta.'''

    ## Explicacion de la app en sidebar con botton
    # with st.sidebar.info(''):
    #         if st.button('Uso de app'):
    #             st.write(response_generator(explicacion)) 
                
    ## configuracion de app            
    st.sidebar.info(markdown)
    st.sidebar.info("Github: [Br1Rdz](%s)" % url)
    logo = "./Clicker.jpg"
    st.sidebar.image(logo)
    
    ##Tabla sin sueldos NaN
    valores = df_ofertas_laborales['Sueldo'].dropna()
    
    #todas las ofertas laborales
    if Campo_laboral == '':
        
        #Explicacion de la app
        with st.expander('Uso de la app'):
            if st.button("Click me"):
                st.write(response_generator(explicacion)) 

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
         
        st.header(f'{len(df_ofertas_laborales)} ofertas laborales para biólogo', divider="gray")
        col1, col2 = st.columns(2)
        ## edicion del tamaño de letra
        st.markdown(
                        """
                    <style>
                    [data-testid="stMetricValue"] {
                        font-size: 12px;
                    }
                    </style>
                    """,
                        unsafe_allow_html=True,
                    )
        with col1:
            st.metric(label= f'Sueldo mínimo mensual', 
                      value= f'${round(min(valores)):,}')
        with col2:
            st.metric(label= f'Sueldo máximo mensual', 
                      value= f'${round(max(valores)):,}')
            
        with st.expander('# Grupos de sueldos y palabras claves'):
            # https://discuss.streamlit.io/t/how-do-i-align-st-title/1668/7
            st.markdown(
                "<h6 style='text-align: justify;'>Se muestran los grupos formados a partir de las palabras clave \
                y los sueldos de todas las ofertas laborales.</h6>", unsafe_allow_html=True)    
            cluster_sueldo(df_cluster)
        
    #Filtro de las ofertas laborales
    if Campo_laboral != '':
        with st.expander('Que es el ingreso mensual necesario (ENSAFI,2024)'):
            if st.button("Explicacion"):
                st.write(response_generator(ENSAFI)) 
        
        #con markdown        
        # st.markdown("<h6 style='text-align: justify;'>Ingreso necesario para cubrir gastos básicos\
        #         (Encuesta Nacional sobre Finanzas Individuales, 2024).</h6>", unsafe_allow_html=True)
        
        columna1, columna2 = st.columns(2)
        ## edicion del tamaño de letra
        st.markdown(
                        """
                    <style>
                    [data-testid="stMetricValue"] {
                        font-size: 12px;
                    }
                    </style>
                    """,
                        unsafe_allow_html=True,
                    )
        
        with columna1:
            st.write(f'Ingreso en {estado_minimo} es ${round(ingreso_minimo):,} (ENSAFI, 2024)')
        with columna2:
            st.write(f'Ingreso en {estado_maximo} es ${round(ingreso_maximo):,} (ENSAFI, 2024)')
                
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label= f'Mínimo mensual en {estado_minimo}', 
                      value= '${:,}'.format(round(sueldo_minimo)),
                      delta = f'-${sueldo_ingreso_minimo:,}', delta_color="normal")
        with col2:
            st.metric(label= f'Máximo mensual en {estado_maximo}', 
                      value= '${:,}'.format(round(sueldo_maximo)),
                      delta = f'${sueldo_ingreso_maximo:,}', delta_color="normal")
                    #   delta = '-${:,}'.format(round((sueldo_maximo - sueldo_minimo))))
            
    # st.balloons()
    with st.spinner('Espera mientras elaboró el mapa...'):  
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
            
            df_filled = df_filtrada.fillna('No disponible') ## sale un warning
            
            st.dataframe(df_filled,
                            column_order=('Nombre', 'Ciudad', 'Sueldo', 'Ingreso_mensual'), ## Hay que agragar la de ingreso_mensual
                            hide_index = True,
                            width = 800,
                            height = 200,
                            column_config={
                            "Nombre": st.column_config.TextColumn(
                                "Puesto",
                                help="Nombre del puesto"
                                # width="none",
                                # required=True
                                ),
                            "Ciudad": st.column_config.TextColumn(
                                "Localidad",
                                help="Ubicación del puesto"
                                # width="none",
                                # required=True
                                ),
                            "Sueldo": st.column_config.NumberColumn(
                                "Sueldo (mensual)",
                                help="Sueldo del puesto",
                                format="$%d"
                                # width="none",
                                # required=True
                                # min_value=0,
                                # max_value=max(df_filtrada.Sueldo),
                            ),
                            "Ingreso_mensual": st.column_config.NumberColumn(
                                "Ingreso (ENSAFI,2024)",
                                help="Ingreso minimo necesario",
                                format="$%d"
                                # width="none",
                                # required=True
                                # min_value=0,
                                # max_value=max(df_filtrada.Ingreso_mensual),
                            )
                            },
                            use_container_width = True
                        )   
                    

if __name__ == '__main__':
    main()