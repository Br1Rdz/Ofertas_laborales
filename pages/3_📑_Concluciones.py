import streamlit as st 

st.set_page_config(page_title="Concluciones", 
                    page_icon="📑", 
                    layout="wide",
                    initial_sidebar_state="collapsed",
                    menu_items=None)
hide_st_style = '''
                    <style>
                    #Main Menu {visibility:hidden;}
                    footer {visibility:hidden;}
                    header {visibility:hidden;}
                    </style>
    '''
st.markdown(hide_st_style, unsafe_allow_html= True)

st.logo("./Informacion.png", icon_image="./info2.png")

st.markdown("<h1 style='text-align: center; color: white;'>Conclusión</h1>", unsafe_allow_html=True)

st.markdown(
    """
<div style="text-align: justify;">
    <ul>
        <li>Durante los meses de <span style="color:orange;">abril y mayo de 2025</span> se recopilaron 530 ofertas laborales dirigidas a biólogos.
        Sin embargo, 297 de estas no reportaron información salarial o presentaban valores atípicos,
        por lo que solo 233 ofertas fueron consideradas para el análisis detallado.</li>
        <li>La cobertura geográfica de las ofertas fue desigual. Se identificaron al menos una oferta en 22 de las 32 entidades
        federativas, mientras que las 10 entidades restantes no registraron ninguna vacante durante el periodo evaluado.</li>
        <li>Los sueldos ofrecidos para biólogos oscilaron entre <span style="color:orange;">$6,000 y $22,000 pesos mensuales</span>.
        La entidad con los sueldos más altos reportados fue Nuevo León, lo que sugiere una mejor remuneración relativa en dicha región.</li>
        <li>El análisis de palabras clave y sueldos promedio permitió identificar tres grupos.
        Términos como “químico”, “farmacéutico” y “laboratorio” (asociados a laboratorio) 
        tiene rango de sueldos promedio entre <span style="color:orange;">$12,000 y $15,000 pesos mensuales</span>.
        No obstante, se reconoce la necesidad de refinar el análisis semántico,
        ya que algunas palabras incluidas podrían no tener una relevancia significativa.</li>
        <li>El Estado de México fue la entidad federativa con el mayor número de vacantes,
        registrando un total de 70 ofertas. Sin embargo, esta entidad también presentó una discrepancia
        entre el sueldo promedio ofrecido y el ingreso necesario mensual estimado por ENSAFI (2024),
        con una diferencia de <span style="color:red;">$5,141 pesos</span>.</li>
        <li>Se identificó una discrepancia entre los sueldos promedio ofrecidos y el ingreso mensual necesario estimado por ENSAFI (2024)
        en <span style="color:orange;">18 de las 22 entidades federativas evaluadas</span>.
        La Ciudad de México presentó la diferencia más pronunciada entre ambos valores.</li>
        <li>La categoría laboral mejor representada fue la de “laboratorio”, que concentró 194 ofertas con sueldos
        que variaron entre <span style="color:orange;">$6,000 y $22,000 pesos</span>. Esta categoría no solo fue la más frecuente,
        sino también la que mostró una mayor amplitud en el rango salarial,
        lo que refleja la diversidad de responsabilidades dentro del área.</li>
        <li>Las ofertas analizadas provienen de los meses de <span style="color:red;">abril y mayo del 2025 de las plataformas OCC y Computrabajo</span>,
        lo cual podria limitar la representatividad del análisis. Aun así, se observa una tendencia clara hacia las actividades técnicas
        de laboratorio. Este hallazgo sugiere que los estudiantes de biología que deseen insertarse en el mercado laboral deberían priorizar
        la adquisición de habilidades prácticas y técnicas especializadas en dichas áreas.
        No obstante, la amplia variabilidad en los sueldos refleja que estas habilidades pueden estar asociadas tanto
        a tareas operativas básicas como a responsabilidades de gestión,
        lo que refuerza la <span style="color:red;">importancia de una formación integral y avanzada</span>.</li>
    </ul>
</div>
    """,
    unsafe_allow_html=True
)

st.markdown("<h1 style='text-align: center; font-size: 25px; color: white;'>✨Gracias por tu apoyo✨</h1>", unsafe_allow_html=True)
