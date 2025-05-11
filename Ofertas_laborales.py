import streamlit as st 
import pandas as pd
import folium
from streamlit_folium import st_folium
import time
import nltk
import plotly.express as px
from sklearn.cluster import KMeans
import sklearn.cluster as cluster
from sklearn.linear_model import LinearRegression

APP_TITLE = 'Ofertas laborales en México'
APP_SUB_TITLE = 'Fuente de OCC y Computrabajo'

# ----------------- Uso de app -------------------
def response_generator(texto):
    '''Esta funcion es para mostrar texto letra por letra con un retraso'''
    for letra in texto.split():
        yield letra + " "
        time.sleep(0.2)  

# ----------------- FILTRADO -------------------
def base_filtrada(df):
    '''Esta funcion realiza filtros a la base de datos a partir de los requerimentos del usuario'''
    
    lista_laboral = [''] + list(df['Relación_profesional'].unique())
    lista_laboral.sort()
    Campo_laboral = st.sidebar.selectbox('Relación profesional', lista_laboral)  
        
    if Campo_laboral:
        df = df[df['Relación_profesional'] == Campo_laboral]      
    
    #numero de filas con coencidencia
    numero = len(df)
    
    if Campo_laboral:
        st.subheader(f'{numero} ofertas laborales para {Campo_laboral}', divider="gray")

    return df, Campo_laboral

# ----------------- Metrica -------------------
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
    # Verificar que hay datos
    if df.empty:
        st.warning("No hay datos para mostrar el mapa.")
        return
    
    map = folium.Map(location=[23.6345, -102.5528], zoom_start=5, scrollWheelZoom=False, tiles="cartodb positron")
    
    choropleth = folium.Choropleth(
        geo_data='./georef-mexico-state@public2.geojson',
        name="Ofertas",
        data=df,
        columns=['Estado', 'Conteo'],  
        key_on='feature.properties.sta_name', 
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
    
    choropleth.geojson.add_child(
        folium.features.GeoJsonTooltip(
            fields=["sta_name"],
            labels=False
            ))
    st_map = st_folium(map, width=700, height=450,  key="map", use_container_width=True, returned_objects=["last_object_clicked"])
    
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
    fig = px.bar(tabla, x='Palabra', y='Frecuencia',color='Palabra',
                 title= f'Top 5 de palabras más frecuentes para {filtro}')
    fig.update_layout(showlegend=False)
    fig.update_traces(width=0.5)  
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

    model = cluster.KMeans(n_clusters=4, init='k-means++')
    kmeans = model.fit(selected_data)

    df['Grupo'] = (kmeans.labels_ + 1).astype(str)

    fig = px.scatter(df, x='Sueldo', y='Frecuencia', color='Grupo',
                    hover_data= 'Palabra',
                    color_discrete_sequence=px.colors.qualitative.G10,
                    category_orders={"Grupo": ["1", "2", "3", "4"]},
                    title="Sueldos y palabras claves")
    fig.update_layout(
    title={
        'x': 0.5,
        'xanchor': 'center'
        }
    )

    return st.plotly_chart(fig, use_container_width=True)

# ----------------- MAIN -------------------
def main():
    '''Funcion principal de la applicacion'''
    #-------- configuracion de pagina ------------  
    
    st.set_page_config(APP_TITLE, layout = 'center', initial_sidebar_state = "collapsed") # esto es por si sale un espacio entre mapa y gráfico de barras
    st.title(APP_TITLE)
    st.caption(APP_SUB_TITLE)
    
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
    df_ofertas_laborales = pd.read_csv('./Tablas_entrada/Tabla_concatenada.csv') # hay que quitar los outlier
    df_cluster = pd.read_csv('./Tablas_entrada/Tabla_cluster.csv') ## Tabla para los grupos por frecuencia y sueldo
    
    #Filtro y mapa
    df_filtrada, Campo_laboral = base_filtrada(df_ofertas_laborales)
    
    sueldo_minimo, estado_minimo, estado_maximo, sueldo_maximo = sueldo_min_max_estado(df_filtrada)
    
    ingreso_minimo:int = ingreso_mensual(df_filtrada, estado_minimo)
    ingreso_maximo:int = ingreso_mensual(df_filtrada, estado_maximo)
    
    sueldo_ingreso_minimo:int = round(ingreso_minimo - sueldo_minimo)
    sueldo_ingreso_maximo:int = round(sueldo_maximo - ingreso_maximo)
    
    ## variable de uso de app
    explicacion = '''Esta aplicación utiliza información recopilada de ofertas laborales 
                   para biólogx de los portales OCC y Computrabajo. 
                   Selecciona de la barra lateral la 'Relación profesional' para comenzar.'''
    
    ENSAFI = ''' En promedio, un mexicano necesita un ingreso mensual de $16,421 para cubrir sus gastos básicos,
                 según la Encuesta Nacional sobre Finanzas Individuales (ENSAFI, 2024).
                 El ingreso necesario para cubrir gastos básicos puede variar dependiendo de la región,
                 el tamaño del hogar y el estilo de vida. Los gastos básicos que pueden incluirse en el presupuesto son:
                 Comida, vivienda, servicios, transporte, educación y vestimenta.'''
                
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
            st.markdown(
                "<h6 style='text-align: justify;'>Se muestran los grupos formados a partir de las palabras clave \
                y los sueldos de todas las ofertas laborales.</h6>", unsafe_allow_html=True)    
            cluster_sueldo(df_cluster)
        
    #Filtro de las ofertas laborales
    if Campo_laboral != '':
        with st.expander('Que es el ingreso mensual necesario (ENSAFI,2024)'):
            if st.button("Explicacion"):
                st.write(response_generator(ENSAFI)) 
        
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
                    
    with st.spinner('Espera mientras elaboró el mapa...'):  
            display_map(df_filtrada)
            
    if Campo_laboral != '':
        grafico_barras(df_filtrada, Campo_laboral)
                
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
                                    ),
                                "Ciudad": st.column_config.TextColumn(
                                    "Localidad",
                                    help="Ubicación del puesto"
                                    ),
                                "Sueldo": st.column_config.NumberColumn(
                                    "Sueldo (mensual)",
                                    help="Sueldo del puesto",
                                    format="$%d"
                                ),
                                "Ingreso_mensual": st.column_config.NumberColumn(
                                    "Ingreso (ENSAFI,2024)",
                                    help="Ingreso minimo necesario",
                                    format="$%d"
                                )
                                },use_container_width = True
                            )   
                        

if __name__ == '__main__':
    main()
