import streamlit as st 

st.set_page_config(page_title="BioEmpleo", 
                    page_icon="🌿", 
                    layout="wide",
                    initial_sidebar_state="collapsed",
                    menu_items=None)

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

st.sidebar.info(markdown)
st.sidebar.info("Github: [Br1Rdz](%s)" % url)

logo = "./LOGO.png"
st.sidebar.image(logo) 
st.logo("./Informacion.png", icon_image="./info2.png")

st.title('Instrucciones')
# https://github.com/streamlit/streamlit/issues/2338

st.markdown(
    """
<div style="text-align: justify;">
    <span style="color:orange;">Funcionalidades de la App:</span>
    <br>
    <ul>
    Esta aplicación utiliza información recopilada de ofertas laborales de los portales
    <span style="color:red;">OCC y Computrabajo</span> dirigidas a biólogos y biólogas 
    para los meses de Mayo y Abril del 2025.
    <br>
        Analiza los datos y presenta visualizaciones interactivas que permiten:
    <li>
        <span style="color:orange;">Mapa de distribución geográfica:</span> Muestra la ubicación de las ofertas laborales.
    </li>
    <li>
        <span style="color:orange;">Análisis de palabras clave:</span> Genera gráficos de barras con las palabras más frecuentes en las descripciones de los puestos.
    </li>
    <li>
        <span style="color:orange;">Comparación salarial:</span> Presenta un gráfico de barras que contrasta los salarios ofrecidos
        con los ingreso mensual necesario <a href="https://es.linkedin.com/posts/rodrigoehlers_cu%C3%A1nto-cuesta-vivir-en-cada-estado-en-2025-activity-7288245570329001984-0yuY" target="_blank" style="color:#04fcb5; text-decoration:underline;">
        ENSAFI, 2024</a>
    </li>
    <li>
        <span style="color:orange;">Análisis de clusters:</span> Agrupa las ofertas laborales en clusters basados en las palabras clave y los salarios promedios
    </li>
    <li>
        <span style="color:orange;">Predicción de sueldo:</span> Predicción de sueldo a partir de la localidad y relación profesional, por medio de Random Forest Regression.
    </li>
    </ul>
</div>
""",
    unsafe_allow_html=True
)    
    
st.markdown(
    """
<div style="text-align: justify;">
    <span style="color:orange;">Para iniciar:</span>
    <br>
    Desde la barra lateral, selecciona las distintas opciones:
    <ul>
        <li>
        <span style="color:orange;">Ofertas laborales.</span> Información de ofertas laborales para biólogos y biólogas en México.
        <br>* Posteriormente seleccione la <span style="color:red;">Relación profesional</span> para explorar las diferentes categorias. 
        <br>* <span style="color:red;">Nota:</span> Las categorias se desarrollarón basondose en el apartado <span style="color:red;">Campo de trabajo</span> de este sitio:
        <a href="https://mx.fcbujed.com/mx/carrera-de-biologo" target="_blank" style="color:green; text-decoration:underline;">FCB-UJED</a> 
        </li>
    </ul>
</div>
""",
    unsafe_allow_html=True
)    
