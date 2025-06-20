$\color{red}\LARGE{\textsf{Analisis de Ofertas laborales para Biologos}}$

> [!NOTE]
> <div align="justify"> La app usa información recopilada por medio de <span style="color:orange;">web scraping</span> de portales de ofertas laborales para "Biologxs" para los meses de abril y mayo del 2025. La información fue limpiada y almacenada para su visualización</div> 
  
  
  
  
  imagenes de las siguientes tortugas <i><b>Gopherus flavomarginatus</b></i>, <i><b>Terrapene coahuila</b></i>, <i><b>Trachemys scripta</b></i> y <i><b>Kinosternon flavescens</b></i>. Usa un <b>dataset</b> para cada una de las clases (especie) de ~ 201 - 300 imagenes, las imagenes se redimensionaron a <b>224 x 224</b>, para su pre-entreno, el tamaño del procesamiento por lote (batch) fue de 32. Adicionalmente se añadadio <b>Data Augmentation</b> para la creacion de datos sinteticos, con la finalidad de aumentar las posibles variaciones de texturas, anchos, alturas, zoom, brillo y orientacion de las imagenes del dataset. Debido a los pocos datos que tiene el <b>"dataset"</b> se opto por crear un modelo de pre-entreno (Pretrained Model for Transfer Learning) usando el modelo de <b>ResNet50</b>, asi tambien se usaron funsiones de activacion como lo fue <b>relu</b>, <b>softmax</b> y el optimizar <b>"adam"</b>, el modelo desempeño despues de 10 epocas se obtuvo los siguientes valores:</div>   
|`Precisión` | `Validacion de precisión` | `Perdida` | `Validacion de perdida`|
| :---:      |           :---:           | :---:     | :---:                  |
|    1.0     |          0.86             |   0.059   |           0.39         |
  
> [!TIP]
> Si usas GPU la clasificacion es mas rapido minimo de 2 Gbs

> [!IMPORTANT]
> Instrucciones
> 
> 1. Intala python >= 3.10
> > Opciones para descargar el repositorio   
> > * Puedes descargar el repertorio desde **"<> code"** y despues seleccionar la opcion de **"Download zip"** 
> > * Clona el repertorio "git clone" https://github.com/Br1Rdz/Classification_turtle.git en alguna carpeta de tu eleccion
> 2. Instalacion de las dependencias a usar pip install -r requirements.txt
> 3. Ejecuta la aplicación streamlit run Classification_turtle.py
> 4. Añade la imagen a clasificar
> 5. FELICIDADES AQUI ESTA TU CLASIFFICACION
> 6. La aplicacion tambien tiene un chatbot sobre datos generales de las especie
> 7. ESPERO DISFRUTES LA APP

> [!WARNING]
> si por alguna razon no se descarga el archivo **turtle_model_V_1_7.keras** (250 mb) debes descargarlo de forma manual.

> [!CAUTION]
> En PC que no tenga una tarjeta de video posiblemente no funcione.
