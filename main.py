#GRUPO CONFORMADO POR:

# SOFÍA YORIO
# ANTONELLA GRASSI
# BRUNO CARDAMONE

# -------------------------------------------------------------------------

# Importamos los módulos necesarios:
import requests
from os import read
from logging import disable
import streamlit as st
import csv
from collections import defaultdict
from streamlit_extras.stylable_container import stylable_container
from streamlit_option_menu import option_menu
from math import *
import pydeck as pdk

# -------------------------------------------------------------------------


#Función para leer el archivo .CSV y 'cachear' los datos:
@st.cache_data
def read_csv():
    """
  Diseño de datos:
  diccionario: dict

  Signatura:
  read_csv: None -> Tuple[list,dict]

  Próposito:
  Recibe un archivo csv, lo lee y retorna una tupla, que contiene 2 elementos: Una lista que contenga los encabezados (los ID) y otro, un diccionario donde cada clave es el ID y cada valor es la información relacionada a ese ID (almacenada en forma de lista).
  Para acceder a los valores de un ID especifico se usará: diccionario[ID]

  -En caso de no poder acceder al archivo .CSV, nos devolverá una tupla con una lista y diccionario vacíos.

  Ejemplos:
 * Si quisieramos abrir un archivo que contiene a alumnos con sus respectivos datos:
  read_csv() -> (["nombre","apellido","edad"], {"nombre":["sofia","antonella"],"apellido":["yorio","grassi"],"edad":[19,19]})

 * Si quisieramos abrir un archivo mas éste nos tira error/no es posible abrirlo correctamente: 
  read_csv() -> ([],{})
  """

    #Realiza la solicitud GET, con el dataset en formato .CSV:
    response = requests.get(
        'https://docs.google.com/spreadsheets/d/1alQCEmWB44HVaNkOZamE_g5VH72lGsmiOPtelJsLQCA/export?format=csv'
    )

    #Verificación de la solicitud:
    if response.status_code == 200:

        #devuelve un diccionario
        data = defaultdict(list)

        #Decodificamos su contenido:
        contenido = response.content.decode("utf-8")

        #Itera sobre las filas del archivo(lo lee)
        reader = csv.reader(contenido.splitlines())
        encabezados = next(reader)

        for fila in reader:
            for indice, encabezado in enumerate(encabezados):
                data[encabezado].append(fila[indice])

        return encabezados, data
    else:
        return [], {}


# -------------------------------------------------------------------------
# Resolución Página 1 - Mapa, según filtros dados:


# Selectores de filtros:
def checkTipo(dataMain):
    """
    Diseño de datos:
    dataMain: Tuple(list,dict)
    tipo: list[str]

    Signatura:
    checkTipo: Tuple(list,dict) -> str

    Próposito: 
    Genera una lista de provincias, para que el usuario pueda seleccionar una de ellas mediante un selectbox y luego retorna la opción elegida.

    Ejemplo:
    Diccionario_Ejemplo =
    {"provincia":["Buenos Aires","Córdoba","Santa Fe","Buenos Aires","Salta","San Juan"],
    "empresa": ["Pretosar","Chabas","Pegorine","Presenti","Maipu","Filippine" ], 
    "precio": ["100.0","303.0","456,89","1876","976.4","59.4"], 
    "producto": ["Gas Oil","Premium","Gas Oil", "Gas Oil", "Premium", "Gas Oil"]
    "latitud": ["-32.6754", "41.8925"," -14.3026", "22.5378", "55.0341", "-5.9337"]  
    "longitud": ["-58.6415", "12.5113", "-170.7106", "114.0165", "-3.4388", "-75.0152"]}

    checkTipo(Diccionario_Ejemplo)
    Entrada (por multiSelect): ["Pretosar"]. -> Salida: ["Pretosar"].
    Entrada (por multiSelect): ["Pretosar","Chabas"]. -> Salida: ["Pretosar","Chabas"].
    """
    header, data = dataMain
    # Crea una lista de provincias posibles, incluyendo la opción de Todas las provincias.
    result = []
    tipos = []
    valor = []
    for tipo in data["producto"]:
        if tipo not in tipos:
            # checkBox de Streamlit
            opcion = st.checkbox(tipo)
            tipos.append(tipo)
            result.append((tipo, opcion))

    for tipo, opcion in result:
        if opcion:
            valor.append(tipo)

    return valor


def selectorEmpresa(dataMain):
    """
    Diseño de datos:
    dataMain: Tuple(list,dict)
    empresas: list[str]

    Signatura:
    selectorEmpresa: Tuple(list,dict) -> str

    Próposito: 
    Genera una lista de provincias, para que el usuario pueda seleccionar una de ellas mediante un selectbox y luego retorna la opción elegida.

    Ejemplo:
    Diccionario_Ejemplo =
    {"provincia":["Buenos Aires","Córdoba","Santa Fe","Buenos Aires","Salta","San Juan"],
    "empresa": ["Pretosar","Chabas","Pegorine","Presenti","Maipu","Filippine" ], 
    "precio": ["100.0","303.0","456,89","1876","976.4","59.4"], 
    "producto": ["Gas Oil","Premium","Gas Oil", "Gas Oil", "Premium", "Gas Oil"]
    "latitud": ["-32.6754", "41.8925"," -14.3026", "22.5378", "55.0341", "-5.9337"]  
    "longitud": ["-58.6415", "12.5113", "-170.7106", "114.0165", "-3.4388", "-75.0152"]}

    selectorEmpresa(Diccionario_Ejemplo)
    Entrada (por multiSelect): ["Pretosar"]. -> Salida: ["Pretosar"].
    Entrada (por multiSelect): ["Pretosar","Chabas"]. -> Salida: ["Pretosar","Chabas"].
    """
    header, data = dataMain
    # Crea una lista de provincias posibles, incluyendo la opción de Todas las provincias.
    empresas = []
    for empresa in data["empresa"]:
        if empresa not in empresas:
            empresas.append(empresa)

    # MultiSelect de Streamlit
    opcion = st.multiselect("-",
                            empresas,
                            placeholder="Seleccione una Empresa: ",
                            default=None,
                            key="multiSelecEmpresa",
                            label_visibility="collapsed")
    return opcion


def selectorProvincia(dataMain):
    """
    Diseño de datos:
    dataMain: Tuple(list,dict)
    provincias: list[str]

    Signatura:
    selectorProvincia: Tuple(list,dict) -> str

    Próposito: 
    Genera una lista de provincias, para que el usuario pueda seleccionar una de ellas mediante un selectbox y luego retorna la opción elegida.

    Ejemplo:
    Diccionario_Ejemplo =
    {"provincia":["Buenos Aires","Córdoba","Santa Fe","Buenos Aires","Salta","San Juan"],
    "empresa": ["Pretosar","Chabas","Pegorine","Presenti","Maipu","Filippine" ], 
    "precio": ["100.0","303.0","456,89","1876","976.4","59.4"], 
    "producto": ["Gas Oil","Premium","Gas Oil", "Gas Oil", "Premium", "Gas Oil"]
    "latitud": ["-32.6754", "41.8925"," -14.3026", "22.5378", "55.0341", "-5.9337"]  
    "longitud": ["-58.6415", "12.5113", "-170.7106", "114.0165", "-3.4388", "-75.0152"]}

    selectorProvincia(Diccionario_Ejemplo)
    Entrada (por selectbox): "Buenos Aires". -> Salida: "Buenos Aires".
    Entrada (por selectbox): "Santa Fe". -> Salida: "Santa Fe".
    """
    header, data = dataMain
    # Crea una lista de provincias posibles, incluyendo la opción de Todas las provincias.
    provincias = [
        "TODAS",
    ]
    for provincia in data["provincia"]:
        if provincia not in provincias:
            provincias.append(provincia)

    # Selectbox de Streamlit
    opcion = st.selectbox("-",
                          provincias,
                          placeholder="Seleccione una provincia: ",
                          index=None,
                          key="selectorProvincia",
                          label_visibility="collapsed")
    return opcion


def selectorPrecioMin(dataMain):
    """
    Diseño de datos:
    dataMain: Tuple(list,dict)
    precios: list[float]

    Signatura:
    selectorPrecioMin: Tuple(list,dict) -> float

    Próposito: 
    Encuentra el rango de precios desde el más bajo hasta el más alto, y permite que el usuario seleccione el precio minimo que quiera ver en el mapa mediante un slider.

    Ejemplo:
    Diccionario_Ejemplo =
    {"provincia":["Buenos Aires","Córdoba","Santa Fe","Buenos Aires","Salta","San Juan"],
    "empresa": ["Pretosar","Chabas","Pegorine","Presenti","Maipu","Filippine" ], 
    "precio": ["100.0","303.0","456,89","1876","976.4","59.4"], 
    "producto": ["Gas Oil","Premium","Gas Oil", "Gas Oil", "Premium", "Gas Oil"]
    "latitud": ["-32.6754", "41.8925"," -14.3026", "22.5378", "55.0341", "-5.9337"]  
    "longitud": ["-58.6415", "12.5113", "-170.7106", "114.0165", "-3.4388", "-75.0152"]}

    selectorPrecioMin(Diccionario_Ejemplo)
    Entrada (por slider): "670". -> Salida: 670.0
    Entrada (por slider): "784". -> Salida: 784.0
    """
    header, data = dataMain
    precios = []
    # Crea una lista con todos los precios
    for precio in data["precio"]:
        precios.append(floor(float(precio)))

    # Encuentra el rango de precios desde el más bajo hasta el más alto
    precioMin = min(precios)
    precioMax = max(precios)

    # Slider de Streamlit
    precio_min = st.slider("Precio Mínimo",
                           precioMin,
                           precioMax,
                           precioMin,
                           label_visibility="visible")
    return float(precio_min)


def selectorPrecioMax(dataMain):
    """
    Diseño de datos:
    dataMain: Tuple(list,dict)
    precios: list[float]

    Signatura:
    selectorPrecioMax: Tuple(list,dict) -> float

    Próposito: 
    Encuentra el rango de precios desde el más bajo hasta el más alto, y permite que el usuario seleccione el precio máximo que quiera ver en el mapa mediante un slider.

    Ejemplo:
    Diccionario_Ejemplo =
    {"provincia":["Buenos Aires","Córdoba","Santa Fe","Buenos Aires","Salta","San Juan"],
    "empresa": ["Pretosar","Chabas","Pegorine","Presenti","Maipu","Filippine" ], 
    "precio": ["100.0","303.0","456,89","1876","976.4","59.4"], 
    "producto": ["Gas Oil","Premium","Gas Oil", "Gas Oil", "Premium", "Gas Oil"]
    "latitud": ["-32.6754", "41.8925"," -14.3026", "22.5378", "55.0341", "-5.9337"]  
    "longitud": ["-58.6415", "12.5113", "-170.7106", "114.0165", "-3.4388", "-75.0152"]}

    selectorPrecioMax(Diccionario_Ejemplo)
    Entrada (por slider): "670". -> Salida: 670.0
    Entrada (por slider): "784". -> Salida: 784.0
    """
    header, data = dataMain
    precios = []
    # Crea una lista con todos los precios
    for precio in data["precio"]:
        precios.append(ceil(float(precio)))

    # Encuentra el rango de precios desde el más bajo hasta el más alto
    precioMin = min(precios)
    precioMax = max(precios)

    # Slider de Streamlit
    precio_max = st.slider("Precio Máximo",
                           precioMin,
                           precioMax,
                           precioMax,
                           label_visibility="visible")
    return float(precio_max)


# Filtrado:
def getdataMap(valor, newData, datatype, precio=None):
    """
    Diseño de datos:
    valor: str or float
    newData: dict
    datatype: str
    precio: str
    index_notInFilter: list

    Signatura:
    getdataMap: (str or float,dict,str,str) -> dict

    Próposito:
    Está función es la encargada en filtrar los datos para que después puedan ser mostrados en el mapa. Su objetivo es sacar del diccionario cada ubicación que no cumpla con el filtro dado por el usuario. Es decir, si el usuario selecciona una provincia(datatype), por ejemplo Buenos Aires(valor), entonces sacará del diccionario cada ubicación, utilizando su index, cuyo valor de la clave "provincia" no sea Buenos Aires.
    Para hacer esto, primero crea una lista (index_notInFilter) con todos los indices de las ubicaciones que no cumplen con el filtro, y luego elimina cada uno de esos indices en cada clave del diccionario relevante para los filtros.

    Ejemplo:
    Diccionario_Ejemplo =
    {"provincia":["Buenos Aires","Córdoba","Santa Fe","Buenos Aires","Salta","San Juan"],
    "empresa": ["Pretosar","Chabas","Pegorine","Presenti","Maipu","Filippine" ], 
    "precio": ["100.0","303.0","456,89","1876","976.4","59.4"], 
    "producto": ["Gas Oil","Premium","Gas Oil", "Gas Oil", "Premium", "Gas Oil"]
    "latitud": ["-32.6754", "41.8925"," -14.3026", "22.5378", "55.0341", "-5.9337"]  
    "longitud": ["-58.6415", "12.5113", "-170.7106", "114.0165", "-3.4388", "-75.0152"]}

    ("Buenos Aires", Diccionario_Ejemplo, "provincia") ->
    {"provincia":["Buenos Aires","Buenos Aires"],
    "empresa": ["Pretosar","Presenti"], # Quedan solamentes los valores que compartan indice
    "precio": ["100.0","1876"],         # con el valor Buenos Aires en la clave "provincia"
    "producto": ["Gas Oil", "Gas Oil"]
    "latitud": ["-32.6754", "22.5378"]  
    "longitud": ["-58.6415", "114.0165"]}

    """
    # Crea una lista vacia para guardar los indices de las ubicaciones que no cumplen con el filtro.
    index_notInFilter = []

    # Revisa si el filtro es de tipo precio.
    if datatype == "precio":
        # Revisa si el valor dado por el usuario es el precio máximo permitido
        if precio == "Max":
            for i in range(len(newData[datatype])):
                # Revisa si el precio de la ubicación es mayor al precio máximo permitido.
                if valor < float(newData[datatype][i]):
                    # Si es así, agrega el indice de esa ubicación a la lista de indices que no cumplen con el filtro.
                    index_notInFilter.append(i)

        # Realiza lo mismo que el anterior si el precio es menor o igual al valor dado.
        if precio == "Min":
            for i in range(len(newData[datatype])):
                if valor >= float(newData[datatype][i]):
                    index_notInFilter.append(i)
    elif datatype == "empresa" or datatype == "producto":
        for i in range(len(newData[datatype])):
            # Si no es del tipo precio, simplemente compara si el valor del i-ésimo elemento de la lista de la clave del filtro es distino al valor dado por el usuario.
            if newData[datatype][i] not in valor:
                index_notInFilter.append(i)
    else:
        for i in range(len(newData[datatype])):
            # Si no es del tipo precio, simplemente compara si el valor del i-ésimo elemento de la lista de la clave del filtro es distino al valor dado por el usuario.
            if valor != newData[datatype][i]:
                index_notInFilter.append(i)

    # Elimina las ubicaciones en los indices que no cumplen con el filtro.
    for i in sorted(index_notInFilter, reverse=True):
        del newData["latitud"][i]
        del newData["longitud"][i]
        del newData["provincia"][i]
        del newData["empresa"][i]
        del newData["producto"][i]
        del newData["precio"][i]

    return newData


def test_getdataMap():
    # Función de testeo de getdataMap
    Diccionario_Ejemplo = {
        "provincia": [
            "Buenos Aires", "Córdoba", "Santa Fe", "Buenos Aires", "Salta",
            "San Juan"
        ],
        "empresa":
        ["Pretosar", "Chabas", "Pegorine", "Presenti", "Maipu", "Filippine"],
        "precio": ["100.0", "303.0", "456,89", "1876", "976.4", "59.4"],
        "producto":
        ["Gas Oil", "Premium", "Gas Oil", "Gas Oil", "Premium", "Gas Oil"],
        "latitud":
        ["-32.6754", "41.8925", " -14.3026", "22.5378", "55.0341", "-5.9337"],
        "longitud": [
            "-58.6415", "12.5113", "-170.7106", "114.0165", "-3.4388",
            "-75.0152"
        ]
    }

    assert (getdataMap("Buenos Aires", Diccionario_Ejemplo, "provincia") == {
        "provincia": ["Buenos Aires", "Buenos Aires"],
        "empresa": ["Pretosar", "Presenti"],
        "precio": ["100.0", "1876"],
        "producto": ["Gas Oil", "Gas Oil"],
        "latitud": ["-32.6754", "22.5378"],
        "longitud": ["-58.6415", "114.0165"]
    })
    assert (getdataMap("Pegorine", Diccionario_Ejemplo, "empresa") == {
        "provincia": ["Santa Fe"],
        "empresa": ["Pegorine"],
        "precio": ["456,89"],
        "producto": ["Gas Oil"],
        "latitud": ["-14.3026"],
        "longitud": ["-170.7106"]
    })


# MAPA:


def mapaVacio():
    # Si no existen ubicaciones a destacar, muestra un mapa vacio de Argentina
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=[],
        get_position=["lat", "lon"],
        get_radius=200,
    )
    view_state = pdk.ViewState(latitude=-38.416097,
                               longitude=-63.616672,
                               zoom=3,
                               bearing=0)
    deck = pdk.Deck(layers=[layer], initial_view_state=view_state)
    st.pydeck_chart(deck)


def mapa(dataMain,
         provincia=None,
         empresa=None,
         tipo=None,
         precioMax=None,
         precioMin=None):
    """
    Diseño de datos:
    dataMain: Tuple(list,dict)
    provincia: str
    empresa: str
    tipo: str
    precioMax: float
    precioMin: float
    newData: dict

    Signatura:
    mapa: Tuple(list,str,str,str,float,float) -> None

    Próposito:
    Esta función se encarga de mostrar en pantalla ubicaciones destacadas en un mapa de Argentina en acuerdo a los valores brindados por el usuario, en la funcion pantalla1_Mapa. Esta función crea un nuevo diccionario cuyos valores, originalmente todos los del dataset, son modificados según cada filtro con la función getdataMap, y luego se accede a los valores modificados de latitud y longitud en el diccionario para darle las ubicaciones a destacar al mapa.
    Si no se cumple ningún filtro, se muestra un mapa de Argentina vacio usando pydeck.
    """
    header, data = dataMain
    newData = data

    # Modifica los valores del diccionario newData según los filtros dados
    if provincia and provincia != "TODAS":
        newData = getdataMap(provincia, newData, "provincia")
    if empresa:
        newData = getdataMap(empresa, newData, "empresa")
    if tipo:
        newData = getdataMap(tipo, newData, "producto")
    if precioMax:
        newData = getdataMap(precioMax, newData, "precio", "Max")
    if precioMin:
        newData = getdataMap(precioMin, newData, "precio", "Min")

    # Accede a los valores de latitud y longitud del diccionario newData y crea dos listas
    latitudes = [float(lat) for lat in newData["latitud"] if lat]
    longitudes = [float(lon) for lon in newData["longitud"] if lon]

    # Lista de diccionarios para st.map con las ubicaciones a destacar
    dataUbicacion = [{
        "lat": lat,
        "lon": lon
    } for lat, lon in zip(latitudes, longitudes)]

    if dataUbicacion:
        # Muestra el mapa si existen ubicaciones a destacar en el diccionario
        st.map(dataUbicacion, color="#669bbc90", use_container_width=True)
    else:
        mapaVacio()


# Función para imprimir la pantalla del Mapa:
def pantalla1_Mapa(dataMain):
    col1, col2 = st.columns(2)
    btn1, btn2, btn3, btn4 = st.columns(4)

    st.markdown(
        "<p style='color: white;font-weight:light;font-size:20px;text-align:center;font-style:italic;'>Seleccione los parámetros de interés y presione buscar </br> para poder visualizarlos en el mapa.</p>"
    )
    with stylable_container(key="map_colorable",
                            css_styles="""
                            background-color: #540b0eff;
                            padding:10px;
                            """):
        st.markdown("""<style>
            .main{
                display: flex;
                background: #09293d;
            }
            .block-container {
                width: 80vw !important;
                max-width: 80vw !important;
                height: 105vh !important;
            }
            .stDeckGlJsonChart  {
                margin-left: 1rem;
            }
            .stSelectbox, .stMultiSelect{
                border-radius: 10px 100px / 120px;
                margin-bottom: 10px;
            }
            .stSlider{
                color:white;
            }
            .stButton button{
                background-color: white;
                color: #540b0eff;
                font-weight: bold;
                font-size: 1em;
                border-radius: .2rem;
                outline: none;
                border: solid 2px #003049ff;
                width: 12vw;
                height: 3rem;
            }
            .stButton{
                display: flex;
                justify-content: center;
                gap: 3rem;
            }
        
            .stButton button:hover{
                color:white;
                border: dashed 2px black;
                background:#98cdee;
            }
        
            .stButton button:focus{
                background:#98cdee;
                box-shadow: 1px 1px 10px red;
            }
        </style>""",
                    unsafe_allow_html=True)

    with col1:
        # Columna de los selectores de Filtros
        st.markdown("<p style='color: red;'>PROVINCIA(S):</p>",
                    unsafe_allow_html=True)
        provincia = selectorProvincia(dataMain)
        st.markdown("<p style='color: red;'>EMPRESA(S):</p>",
                    unsafe_allow_html=True)
        empresa = selectorEmpresa(dataMain)
        st.markdown("<p style='color: red;'>TIPO(S):</p>",
                    unsafe_allow_html=True)
        tipo = checkTipo(dataMain)
        st.markdown(
            "<p style='color: white;font-weight:bold;font-size:18px;text-shadow:2px 2px black;'>'PRECIO:</p>",
            unsafe_allow_html=True)
        precioMin = selectorPrecioMin(dataMain)
        precioMax = selectorPrecioMax(dataMain)

        with btn1:
            buscar = st.button("Buscar", type="primary")
        with btn2:
            limpiar = st.button("Limpiar", type="primary")

    with col2:
        # Columna del mapa
        if buscar and not limpiar:  # si se le dio a buscar hace la funcion map
            mapa(dataMain, provincia, empresa, tipo, precioMax, precioMin)
        else:  # si no llama al mapa vacio
            mapaVacio()


# -------------------------------------------------------------------------
# Resolución Página 2 – Línea de tiempo, promedio según el tipo de combustible:


def seleccion_fechas(dataMain):
    """
        Diseño de datos:
        fechas:list

        Sinatura:
        seleccion_fechas: Tuple[list,dict] -> list

        Próposito: A través de la información del dataset obtenido, recolecta las fechas del mismo y luego, las retorna ordenadas de forma ascendiente -- A través de una lista.

        EJEMPLOS:
        * sea data1=(["indice_tiempo","años"],{"indice_tiempo":["2010-04","1991-05","2010-07"],"años":["2010","1991"]})

        seleccion_fechas(data1)==["1991-05","2010-04","2010-07"]

        * sea data2=(["indice_tiempo","meses"],{"indice_tiempo":["2005-04","2004-05","2001-07","1990-07","2004-07","2005-02","2005-06"],"meses":["agosto","julio","junio","septiembre","febrero"]})

        seleccion_fechas(data2)==["1990-07","2001-07","2004-05","2004-07","2005-02","2005-04","2005-06"]

    """
    header, data = dataMain  #obtiene los datos del dataset
    fechas = []

    for x in range(len(data["indice_tiempo"])):
        if data["indice_tiempo"][x] not in fechas:
            fechas.append(data["indice_tiempo"][x])

    fechas = sorted(fechas)  #La ordenamos de menor a mayor

    return fechas


def test_seleccion_fechas():
    data1 = (["indice_tiempo", "años"], {
        "indice_tiempo": ["2010-04", "1991-05", "2010-07"],
        "años": ["2010", "1991"]
    })
    data2 = (["indice_tiempo", "meses"], {
        "indice_tiempo": [
            "2005-04", "2004-05", "2001-07", "1990-07", "2004-07", "2005-02",
            "2005-06"
        ],
        "meses": ["agosto", "julio", "junio", "septiembre", "febrero"]
    })

    assert (seleccion_fechas(data1) == ["1991-05", "2010-04", "2010-07"])
    assert (seleccion_fechas(data2) == [
        "1990-07", "2001-07", "2004-05", "2004-07", "2005-02", "2005-04",
        "2005-06"
    ])


def precios_promedio(gasolina_tipo, date, dataMain):
    """
        Diseño de datos:
        promedio:float
        precios:list

        Signatura:
        precios_promedio:str,str,Tuple[list,dict]->float

        Próposito: Según el tipo de combustible seleccionado y la fecha seleccionada (extraídos del dataset), devuelve el promedio de todos los productos(es decir, las compras del combustible) que correspondan con el anterior criterio

        EJEMPLOS:
        * sea data1=(["indice_tiempo","años","precio","producto"],{"indice_tiempo":["2010-04","2010-04","1991-05","2012-02","2010-04","2010-04","2010-12","2002-01","2002-02","2010-04"],"años":["2010","1991"],"precio":["192","2090","200.4","200","12","14","140","1442","1355","1"],"producto":["GNC","GNC","Nafta (súper) entre 92 y 95 Ron","Gas Oil Grado 3","GNC","GNC","Gas Oil Grado 2","Gas Oil Grado 3","Natfa (súper) entre 92 y 95 Ron","GNC"]})


        precios_promedio("GNC","2010-04",data1)==461.8
        (con precios=["192","2090","12",14","1"])

        * sea data2=(["indice_tiempo","meses","precio","producto"],{"indice_tiempo":["2004-05","2001-07","2024-07","1990-07","2024-07","2024-07","2004-07","2024-07","2005-02","2024-07","2024-07","2005-06","2024-07"],"meses":["agosto","julio","junio","septiembre","febrero"],"precio":["192","2090","200.4","200","12","14","140","1442","1355","1","1","4785","140"],"producto":["GNC","Gas Oil Grado 3","Nafta (premium) de más de 95 Ron","GNC","Nafta (premium) de más de 95 Ron","Nafta (premium) de más de 95 Ron","Nafta (súper) entre 92 y 95 Ron","Nafta (premium) de más de 95 Ron","Gas Oil Grado 3","Nafta (premium) de más de 95 Ron","Nafta (premium) de más de 95 Ron","Gas Oil Grado 2","Nafta (premium) de más de 95 Ron"]})

        precios_promedio("Nafa Premium","2024-07",data2)==258.63
        (con precios=["200.4","14","12","1442","1","1",140])

        * sea data3=(["indice_tiempo","producto","precio"],{"indice_tiempo":["2004-01","2002-03","2002-06"],"producto":["GNC","Gas Oil Grado 2","Gas Oil Grado 3"],"precio":["20","100","4"]})

        precios_promedio("Gas Oil Grado 3","2002-03",data3)==0 
        (con precios=[]) #OPCIÓN EN DONDE LA FECHA NO CONTIENE NINGÚN DATO DE PRECIO.


    """
    header, data = dataMain  #Obtiene los datos del dataset

    if gasolina_tipo == "Nafta Premium":
        gasolina_tipo = "Nafta (premium) de más de 95 Ron"
    elif gasolina_tipo == "Nafta Super":
        gasolina_tipo = "Nafta (súper) entre 92 y 95 Ron"

    #Inicializamos las variables:
    promedio = 0
    precios = []

    for x in range(len(data["precio"])):
        if data["indice_tiempo"][x] == date and data["producto"][
                x] == gasolina_tipo:
            precios.append(float(data["precio"][x]))

    if precios:  #Es decir, si la lista contiene al menos 1 valor
        promedio = round(sum(precios) / len(precios), 2)

    return promedio


def test_precios_promedio():
    data1 = (["indice_tiempo", "años", "precio", "producto"], {
        "indice_tiempo": [
            "2010-04", "2010-04", "1991-05", "2012-02", "2010-04", "2010-04",
            "2010-12", "2002-01", "2002-02", "2010-04"
        ],
        "años": ["2010", "1991"],
        "precio": [
            "192", "2090", "200.4", "200", "12", "14", "140", "1442", "1355",
            "1"
        ],
        "producto": [
            "GNC", "GNC", "Nafta (súper) entre 92 y 95 Ron", "Gas Oil Grado 3",
            "GNC", "GNC", "Gas Oil Grado 2", "Gas Oil Grado 3",
            "Natfa (súper) entre 92 y 95 Ron", "GNC"
        ]
    })

    #precios=["192","2090","12","14","1"]
    assert (precios_promedio("GNC", "2010-04", data1) == 461.8)

    data2 = (["indice_tiempo", "meses", "precio", "producto"], {
        "indice_tiempo": [
            "2004-05", "2001-07", "2024-07", "1990-07", "2024-07", "2024-07",
            "2004-07", "2024-07", "2005-02", "2024-07", "2024-07", "2005-06",
            "2024-07"
        ],
        "meses": ["agosto", "julio", "junio", "septiembre", "febrero"],
        "precio": [
            "192", "2090", "200.4", "200", "12", "14", "140", "1442", "1355",
            "1", "1", "4785", "140"
        ],
        "producto": [
            "GNC", "Gas Oil Grado 3", "Nafta (premium) de más de 95 Ron",
            "GNC", "Nafta (premium) de más de 95 Ron",
            "Nafta (premium) de más de 95 Ron",
            "Nafta (súper) entre 92 y 95 Ron",
            "Nafta (premium) de más de 95 Ron", "Gas Oil Grado 3",
            "Nafta (premium) de más de 95 Ron",
            "Nafta (premium) de más de 95 Ron", "Gas Oil Grado 2",
            "Nafta (premium) de más de 95 Ron"
        ]
    })

    # precios=["200.4","14","12","1442","1","1",140]
    assert (precios_promedio("Nafta Premium", "2024-07", data2) == 258.63)

    data3 = (["indice_tiempo", "producto", "precio"], {
        "indice_tiempo": ["2004-01", "2002-03", "2002-06"],
        "producto": ["GNC", "Gas Oil Grado 2", "Gas Oil Grado 3"],
        "precio": ["20", "100", "4"]
    })

    #precios=[]
    assert (precios_promedio("Gas Oil Grado 3", "2002-03", data3) == 0)


# Función para imprimir la pantalla de la Linea de tiempo
def pantalla2_lineaDeTiempo(dataMain):
    """
        Diseño de datos:

        gasolinas: componente 'radio' extraído del streamlit
        fecha: componente 'slider' extraído del streamlit
        promedio: float

        Signatura:
        pantalla2_lineaDeTiempo: Tuple(list,dict)->None

        Próposito: Mostrar en pantalla una serie de opciones, para que el usuario pueda elegir el tipo de combustible que prefiere, con un slider , donde el usuario podrá desplazarse a la fecha de su interés, y a continuación se le mostrará el promedio usando la función 'precios_promedio'
        -En caso de ser con fecha actual(2024): Se mostrará el mensaje con tiempo verbal en Presente
        -En caso de ser con otra fecha: Se mostrará el mensaje con tiempo verbal en Pasado
        -En caso de no haber ninguna fecha en ese período: Se le indicará a través de un mensaje.

        EJEMPLOS: (ACLARACIÓN, PRETENDAMOS QUE EL RESULTADO DEL PROMEDIO ES EL DEL EJEMPLO DE LA ANTERIOR FUNCIÓN, 'precios_promedio')
        **precios_promedio("GNC","2010-04",data1)==461.8
        **precios_promedio("Nafta Premium","2024-07",data2)==258.63
        **precios_promedio("Gas Oil Grado 3","2002-03",data3)==0

        * sea data1=(["indice_tiempo","años","precio","producto"],{"indice_tiempo":["2010-04","2010-04","1991-05","2012-02","2010-04","2010-04","2010-12","2002-01","2002-02","2010-04"],"años":["2010","1991"],"precio":["192","2090","200.4","200","12","14","140","1442","1355","1"],"producto":["GNC","GNC","Nafta (súper) entre 92 y 95 Ron","Gas Oil Grado 3","GNC","GNC","Gas Oil Grado 2","Gas Oil Grado 3","Natfa (súper) entre 92 y 95 Ron","GNC"]})


        pantalla2_lineaDeTiempo(data1) -> (Se mostrará en pantalla): "El promedio fue: $461.8"

        * sea data2=(["indice_tiempo","meses","precio","producto"],{"indice_tiempo":["2004-05","2001-07","2024-07","1990-07","2024-07","2024-07","2004-07","2024-07","2005-02","2024-07","2024-07","2005-06","2024-07"],"meses":["agosto","julio","junio","septiembre","febrero"],"precio":["192","2090","200.4","200","12","14","140","1442","1355","1","1","4785","140"],"producto":["GNC","Gas Oil Grado 3","Nafta (premium) de más de 95 Ron","GNC","Nafta (premium) de más de 95 Ron","Nafta (premium) de más de 95 Ron","Nafta (súper) entre 92 y 95 Ron","Nafta (premium) de más de 95 Ron","Gas Oil Grado 3","Nafta (premium) de más de 95 Ron","Nafta (premium) de más de 95 Ron","Gas Oil Grado 2","Nafta (premium) de más de 95 Ron"]})

        pantalla2_lineaDeTiempo(data2) -> (Se mostrará en pantalla): "El promedio es: $258.63"

        * sea data3=(["indice_tiempo","producto","precio"],{"indice_tiempo":["2004-01","2002-03","2002-06"],"producto":["GNC","Gas Oil Grado 2","Gas Oil Grado 3"],"precio":["20","100","4"]})

        pantalla2_lineaDeTiempo(data3) -> (Se mostrará en pantalla): "No hubo ningún registro de precios en esa fecha."

    """
    fechas_opcion = seleccion_fechas(dataMain)

    with st.container():
        st.title("Línea del tiempo")
        st.subheader(
            "Podrás visualizar cuál fue el promedio, según el tipo del combustible que usted eliga, a lo largo de los años"
        )

        st.divider()

        with stylable_container(key="radio_coloreable",
                                css_styles="""
                                    {
                                    background-color: white;
                                    }"""):
            st.write("")  #Para dejar espacio y no se vea apilado.

            gasolinas = st.radio("Selecciona el tipo del combustible:", [
                "GNC", "Gas Oil Grado 2", "Gas Oil Grado 3", "Nafta Super",
                "Nafta Premium"
            ],
                                 index=0,
                                 horizontal=True,
                                 key="radio_gasolinas")

            st.write("")  #Para dejar espacio y no se vea apilado.

            fecha = st.select_slider("-",
                                     options=fechas_opcion,
                                     label_visibility="hidden",
                                     key="fechas_slider")

            #-------------------COLOR RADIO: ---------------

            colorTxT = st.markdown("""<style>input[type="radio"] + div {
                                         background: white !important;
                                     } 
                                    </style>""",
                                   unsafe_allow_html=True)

            colorOnClick = st.markdown(
                """<style>input[type="radio"]:checked + div {
                                     color: #0a5279 !important;
                                     font-weight: bolder;
                                     background: #8dd1f611 !important;
                                     }
                                    </style>""",
                unsafe_allow_html=True)

            colorCircle = st.markdown(
                """<style>div.row-widget.stRadio > div[role="radiogroup"] > label[data-baseweb="radio"] > div{
                                     background: #8ca4fa;
                                     }
                                    </style>""",
                unsafe_allow_html=True)

            #-------------COLOR SLIDER: ----------------------

            colorMinMax = st.markdown(
                """<style> div.stSlider>div[data-baseweb="slider"]>div[data-testid="stTickBar"]>div{
                                    color: #003049ff;
                                    background: white;
                                    }
                                    </style>""",
                unsafe_allow_html=True)

            Slider_Cursor = st.markdown(
                """<style> div.stSlider>div[data-baseweb="slider"]>div>div>div[role="slider"]{
                                        background-color: #540b0eff;
                                        }
                                        </style>""",
                unsafe_allow_html=True)

            Slider_Cursor_hover = st.markdown(
                """<style>div.stSlider>div[data-baseweb="slider"]>div>div>div[role="slider"]:hover{
                                            background-color: #892428;
                                            }
                                            </style>""",
                unsafe_allow_html=True)

            Slider_Number = st.markdown(
                """<style>div.stSlider>div[data-baseweb="slider"]>div>div>div>div{
                                        color:  #540b0eff;
                                        }
                                        </style>""",
                unsafe_allow_html=True)

            ColorSlider = st.markdown(
                """<style>div.stSlider > div[data-baseweb="slider"] > div > div
                                    { 
                                    background: linear-gradient(to right, #003049ff 0%, #09293df5 25%, #669bbc90 75%, #ffffffff 100%);
                                    }
                                    </style>""",
                unsafe_allow_html=True)

            #------------------------------------------------

            promedio = precios_promedio(gasolinas, fecha, dataMain)

            if promedio == 0:
                st.markdown(
                    "<div style='color: black; text-align:center'> No hubo ningún registro de precios en esa fecha. </div>",
                    unsafe_allow_html=True)
            else:
                if "2024" in fecha:
                    st.markdown(
                        f"<div style='text-align: center;'>El promedio es: <span style='color: blue;'>${promedio}</span></div>",
                        unsafe_allow_html=True)
                else:
                    st.markdown(
                        f"<div style='text-align: center;'> El promedio fue: <span style='color: blue;'> ${promedio} </span> </div>",
                        unsafe_allow_html=True)


# -------------------------------------------------------------------------
# Resolución Página 3 – Tabla de Promedio por Provincia:


def promedio_precio(precios, num):
    """
      Diseño de datos: 
      precio: List[Number]
      num: List[Number]
      Signatura: 
      promedio_precio: List[Number] List[Number] -> List[Number]
      Próposito: Toma una lista de suma de precios y divide por la cantidad de veces que se sumaron para obtener un promedió.
      Ejemplos:    
      [100,200,300] 3 -> 200
    """
    for i in range(len(precios)):
        precios[i] = round(precios[i] / num[i], 2)
    return precios


def get_data_table(dataMain):
    """
      Diseño de datos: 
      data: Tuple[list,dict]
      Signatura:
      get_data_table: Tuple[list,dict] -> dict
      Próposito:
      Recibe una tupla que contiene 2 elementos: Una lista que contenga los encabezados y otro, un diccionario donde cada clave es el encabezado correspondiente, y cada valor es la 
      información relacionada a ese encabezado (almacenada en forma de lista).
      Retorna un diccionario que contiene las provincias como claves y los precios promediados
      Ejemplos:
      get_data_table: Tuple[list,dict] -> dict
    """
    # Obtener la lista de provincias
    header, data = dataMain  # obtenemos la lista de encabezados y el diccionario
    resultado = {
        "Provincia": [],
        "Precio Promedio": []
    }  # creamos el diccionario que contendrá los resultados
    indexPromedio = []  # index de precios promedios

    año = data["indice_tiempo"]  # obtenemos la lista de años

    # Recorremos el diccionario para obtener los precios promedios
    for index in range(0, len(año) - 1):
        year = año[index].split("-")  # obtenemos la lista de años
        year = year[0]  # obtenemos el año

        # comparamos si es el año que estamos buscando
        if year == "2024":
            precios = data["precio"][
                index]  # obtenemos un precio a través de un indice
            provincias = data["provincia"][
                index]  # obtenemos una provincia a través de un indice
            precios = float(precios)
            indexProvincias = 0

            # si la provincia no está en el diccionario, la agregamos,agregamosel precio,agremamos un indice al indexPromedio
            if provincias not in resultado['Provincia']:
                resultado['Provincia'].append(provincias)
                resultado['Precio Promedio'].append(precios)

                indexPromedio.append(0)
            else:
                # si la provincia ya está en el diccionario, buscamos su indice y sumamos el precio actual al que ya tiene la provincia y sumamos 1 al indexPromedio
                indexProvincias = resultado['Provincia'].index(provincias)
                resultado['Precio Promedio'][indexProvincias] += precios

                indexPromedio[indexProvincias] += 1

    # Obtenemos el promedio de los precios promedios
    promedio_precio(resultado['Precio Promedio'], indexPromedio)
    return resultado


# Función para imprimir la pantalla de la Tabla
def pantalla3_Tabla(diccionario):
    """
      Diseño de datos:
      diccionario: dict

      Signatura:
      pantalla3_Tabla: dict -> None

      Próposito:
      Recibe un diccionario y genera una tabla que utiliza las claves de ese diccionario como encabezados de la tabla y genera las filas utlizando la información almacenada en los valores del diccionario en forma de lista como cada casillero en la columna de su encabezado (clave) correspondiente.
      """
    # Genera una tabla usando HTML
    table_html = "<table style='border: 2px solid #003049ff; padding: 8px; width: 100%;'>"

    #---------------------- Crea la fila del Encabezado
    table_html += "</tr>"
    for header in diccionario.keys():
        table_html += f"<th style ='border: 1px solid #003049ff; background-color: #09293df5; font-size: 25px; color: white; text-align: center;'> {header} </th>"
    table_html += "</tr>"

    #---------------------- Crea las filas de los datos
    for i in range((len(diccionario["Provincia"]))):
        table_html += "</tr>"
        for key in diccionario.keys():
            table_html += f"<td style ='border: 1px solid #003049ff; background-color: #669bbc90; font-size: 20px; color: #003049; text-align: center;'> {diccionario[key][i]} </td>"
        table_html += "</tr>"

    table_html += "</table>"

    # Muestra la tabla en la pantalla con Streamlit
    with st.container():
        st.title("Tabla de Promedios")
        st.subheader(
            "Tabla del precio promedio del combustible, por provincia, en el año 2024.",
            anchor="100px")
        st.divider()
        st.markdown(table_html, unsafe_allow_html=True)


# -------------------------------------------------------------------------


def main():
    dataMain = read_csv()  #Leemos el dataset una única vez.

    #CÓDIGO DEL MENÚ:

    with st.sidebar:
        menu = option_menu(
            None, ["Inicio", "Mapa", "Línea del tiempo", "Precios Promedios"],
            icons=[
                'bi bi-house-door-fill', 'bi bi-globe-americas',
                "bi bi-clock-history", 'bi bi-coin'
            ],
            menu_icon="cast",
            default_index=0,
            orientation="vertical",
            styles={
                "container": {
                    "padding": "0!important",
                    "background-color": "#09293d",
                    "color": "white"
                },
                "icon": {
                    "color": "#94c9ea",
                    "font-size": "25px"
                },
                "nav-link": {
                    "font-size": "10px",
                    "text-align": "left",
                    "margin": "0px",
                    "--hover-color": " rgba(238, 39, 72, 0.422)",
                    "color": "white"
                },
                "nav-link-selected": {
                    "background-color": "#94c9ea50"
                },
            })

    #SELECCIÓN DE OPCIONES:
    if menu == "Mapa":
        pantalla1_Mapa(dataMain)
    elif menu == "Línea del tiempo":
        pantalla2_lineaDeTiempo(dataMain)
    elif menu == "Precios Promedios":
        pantalla3_Tabla(get_data_table(dataMain))
    else:
        #PANTALLA DE INICIO:

        #Fonts:
        st.markdown("""
                    <link rel="preconnect" href="https://fonts.googleapis.com">
                    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
                    <link href="https://fonts.googleapis.com/css2?family=Dancing+Script:wght@600&display=swap" rel="stylesheet">
                    <link href="https://fonts.googleapis.com/css2?family=LXGW+WenKai+Mono+TC&display=swap" rel="stylesheet">
                    <link href="https://fonts.googleapis.com/css2?family=Caveat:wght@400..700&display=swap" rel="stylesheet">
                    <link href="https://fonts.googleapis.com/css2?family=Nunito:ital,wght@0,200..1000;1,200..1000&display=swap" rel="stylesheet">


                    """,
                    unsafe_allow_html=True)

        #Css:
        css = """<style>
            .title {
                font-size: 50px; 
                text-align:center;
                font-family: "Dancing Script", cursive;
                font-optical-sizing: auto;
                font-weight: 555;
                font-style: normal;
                text-shadow: 5px 2px 21px #0023FF;

            }

            hr {
                border: none;
                height: 1px;
                background-color: #0023FF;
                margin: 20px 0;
            }

            .subheader {
                font-size: 24px;
                font-family: "LXGW WenKai Mono TC", monospace;
                font-weight: 400;
                font-style: normal;
                color: #540b0eff;
                margin-bottom: 10px;
            }

            .subheader_sub{
                            font-size: 25px;
                            font-family: "Caveat", cursive;
                            font-optical-sizing: auto;
                            font-weight: 400;
                            font-style: normal;
                            color: #668aff;
                            margin-bottom: 10px;
                        }

            .write {
                font-size: 18px;
                font-family: "Nunito", sans-serif;
                font-optical-sizing: auto;
                font-weight: <weight>;
                font-style: normal;
                color: #000000;
                margin-bottom: 20px;
                line-height: 1.5;
            }

            .write_sub {
                font-size: 18px;
                font-family: "Nunito", sans-serif;
                font-optical-sizing: auto;
                font-weight: <weight>;
                font-style: normal;
                color: #7d625d;
                margin-bottom: 20px;
                line-height: 1.5;

            }

            .container {
                background-color: #540b0eff;
                padding: 10px;
                border-radius: 10px;
                color: white;
                margin-top: 20px;
                height:400px;
            }

            .container_map{
                background-color: #540b0eff;
                padding: 10px;
                border-radius: 10px;
                color: white;
                margin-top: 20px;
                margin-bottom:20px;
                width:320px;

            }
            </style>
            """

        st.markdown(css, unsafe_allow_html=True)

        #CONTENIDO DEL INICIO:
        st.markdown(
            '<div class="title"> ¡Bienvenid@ a nuestra página web!</div>',
            unsafe_allow_html=True)

        st.divider()

        c1, c2 = st.columns(2)

        with c1:
            st.image("argentina.png", caption="Mapa de Argentina")

        with c2:
            st.markdown(
                '<div class="subheader">¿Qué puedo hacer en está página...?</div>',
                unsafe_allow_html=True)

            st.markdown(
                '<div class="write">Nos preguntábamos qué tanta información se podía sacar de los combustibles en Argentina, y decidimos realizar 3 diferentes puntos de vista:</div>',
                unsafe_allow_html=True)

            with stylable_container(
                    key="Inicio_coloreable",
                    css_styles="""{

                                                                               padding:5px;
                                                                               border-radius: 0px 44px 10px 32px;
            -webkit-border-radius: 0px 44px 10px 32px;
            -moz-border-radius: 0px 44px 10px 32px;
            background: #09293d;
            border: 7px dotted #0c3388;
                                                                                }""",
            ):
                c3, c4 = st.columns(2)

                with c3:
                    st.markdown("""
                                   <div class="container">
                                    <div class="subheader_sub">Precios Promedios</div> 
                                    <div class="write_sub">Aquí, podrás ver cómo cada provincia, tiene un promedio diferente de combustible. Útil para un trabajo investigativo.</div>
                                    </div>""",
                                unsafe_allow_html=True)
                with c4:
                    st.markdown("""
                                   <div class="container">
                                   <div class="subheader_sub">Línea del Tiempo</div>
                                   <div class="write_sub">Acá, podrás ver según el tipo de combustible, el promedio de todos los productos comprados en una partícular fecha. ¡Asombroso!</div></div>""",
                                unsafe_allow_html=True)

                st.markdown("""
                               <div class="container_map">
                               <div class="subheader_sub">El Mapa</div>
                               <div class="write_sub">Y por supuesto, la atracción principal: Podrás realizar una búsqueda personalizada sobre los tipos de combustible, sus empresas y ubicación en Argentina.</div>
                               </div>
                               """,
                            unsafe_allow_html=True)


#EJECUTAR CÓDIGO:
if __name__ == "__main__":
    main()
