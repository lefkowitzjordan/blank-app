
import os
import numpy as np
import pandas as pd
import pydeck as pdk
import rasterio
import streamlit as st
from pyproj import Transformer

APP_TITLE = "Cancer Risk Factor Search"
APP_SUBTITLE = "Environmental insights for informed health decisions"

st.set_page_config(page_title=APP_TITLE, layout="wide")

TIF_PATH = "/mount/src/blank-app/NDVI_california.tif"
CALENV_PATH = "CalEnvScreen.xlsx"
NDVI_STATS_PATH = "/tmp/ndvi_stats.npz"
NDVI_BINS = np.linspace(0.0, 1.0, 2001)

TRANSLATIONS = {
    "en": {
        "lang.select": "Select Language",
        "lang.english": "English",
        "lang.spanish": "Español",
        "nav.home": "Home",
        "nav.ndvi": "NDVI",
        "nav.air_quality": "Air Quality",
        "nav.resources": "Resources",
        "home.banner_title": "Cancer Risk Factor Search",
        "home.intro_1": "Welcome! This Cancer Risk Factor Search tool is designed to help Californians remain informed about the environment around them – and how it can affect the likelihood and outcome of cancer development.",
        "home.intro_2": "California is the most populated state, and one of the most polluted ones too. This means a lot of people are having their health affected by their environment. This tool is based on, and even pulls data from, existing location-based search tools that provide information about environmental exposures like the CalEnviroScreen or the EWG's Tap Water Database. However, these tools are more focused on providing data about a variety of exposures, while the goal of the Cancer Risk Factor Search tool is to take exposure data and provide information about how these relate to a specific health outcome: cancer.",
        "home.intro_3": "Cancer is the second leading cause of death in the US and is the highest NIH-funded disease area. Because of this, there is a lot of research done on cancer, and for good reason too. But most people do not understand how the environment around them can relate to cancer in their body, even though modern science does. Thus, the goal of this tool is to help break down how people could be getting exposed to carcinogens (cancer-causing chemicals) in their day-to-day life, and provide resources to mitigate these effects.",
        "home.intro_4": "This tool helps explain these factors, and provides user-specific information about how they exist in your life, hoping to make this tool even more helpful.",
        "home.search_intro": "Enter coordinates to retrieve vegetation, air quality, and environmental risk data for any California location.",
        "home.coord_label": "Latitude, Longitude",
        "home.coord_placeholder": "e.g. 34.05, -118.25",
        "ndvi.output_title": "Your NDVI output",
        "ndvi.no_data": "No data available for this location",
        "ndvi.percentile_text": "For context, this is the {percentile}th percentile for California (areas with NDVI > 0). The state average is {state_avg}.",
        "btn.whats_ndvi": "What's NDVI?",
        "btn.learn_more_air": "Learn more about air quality",
        "home.map_title": "🗺️ Map",
        "home.map_input_location": "Input location",
        "home.map_pixel_center": "Pixel center",
        "home.map_legend_input": "Input location ({lat}, {lon})",
        "home.map_legend_pixel": "Pixel center ({lat}, {lon})",
        "btn.resources": "📋 Resources",
        "ndvi.title": "What is NDVI?",
        "ndvi.subtitle": "Understanding the Normalized Difference Vegetation Index",
        "ndvi.no_result": "Enter coordinates on the Home page to see your NDVI output here.",
        "ndvi.definition_title": "📖 Definition",
        "ndvi.definition_p1": "NDVI stands for Normalized Difference Vegetation Index. This metric is used to tell how much vegetation (aka living plants) are in a given area. NDVI values are calculated using satellite images that compare the amount of light that plants absorb versus reflect.",
        "ndvi.image_source_eos": "Image source: EOS Data Analytics",
        "ndvi.values_title": "📊 Understanding NDVI Values",
        "ndvi.values_intro": "NDVI values range from −1 to 1:",
        "ndvi.negative_title": "Negative values",
        "ndvi.negative_desc": "Water (bodies of water, clouds, or snow)",
        "ndvi.zero_title": "Values near zero",
        "ndvi.zero_desc": "Limited vegetation, bare soil",
        "ndvi.positive_title": "Positive values",
        "ndvi.positive_desc": "Lots of healthy vegetation",
        "ndvi.cancer_title": "🔬 NDVI & Cancer Research",
        "ndvi.cancer_p1": "Increased NDVI has been found to be protective against cancer mortality. This relationship has been indicated for cancers such as breast cancer, bladder cancer, skin cancer, but especially for prostate and lung cancer.",
        "ndvi.study_link_text": "In one study",
        "ndvi.cancer_p2": "patients with prostate cancer who did not undergo surgery had an increased likelihood of mortality. But patients residing in areas with medium NDVI values (0.217–0.278) had a significantly decreased risk of mortality, and patients in areas with high NDVI values (>0.278) had an even lower risk.",
        "ndvi.cancer_p3": "Overall, NDVI values greater than 0.3 were shown to correlate with a decrease in mortality risk across all cancers. Additionally, increases in NDVI (more vegetation) over time have shown to be protective. So, promoting wildlife and nature growth can be important for your health!",
        "ndvi.learn_more_title": "📚 Learn More",
        "ndvi.learn_more_p": "For more information on NDVI with respect to cancer, we recommend that you {link} that summarizes the research that has been done on the topic. Please note that increased NDVI can by no means completely cure or prevent cancer.",
        "ndvi.learn_more_link_text": "check out this study",
        "ndvi.image_source_earth": "Image source: earth.com",
        "air.title": "Air Quality",
        "air.subtitle": "How air quality affects cancer outcomes",
        "air.no_result": "Enter coordinates on the Home page to see your air quality output here.",
        "air.output_title": "Your air quality output",
        "air.ozone_label": "Ozone (8-hr max)",
        "air.pm25_label": "PM2.5 (annual mean)",
        "air.percentile_word": "percentile",
        "air.ozone_title": "Ozone",
        "air.ozone_what_is": "What is Ozone?",
        "air.ozone_p1": "Ozone, also known as O3, is a highly reactive gas molecule made up of 3 oxygen atoms. For comparison, the typical oxygen we breathe is O2, with only two oxygen atoms. As much as extra oxygen may sound good, this molecule is not stable and can negatively affect the body.",
        "air.ozone_p2": "Ozone is a natural component of the upper atmosphere, but ground-level ozone, which is the ozone that exists where we live and breathe, is not so natural. Ground-level ozone is formed by reactions in the air with nitrogen oxides, volatile organic compounds, and sunlight. The former two are air pollutants, entering the atmosphere through processes such as industrial facility emissions, gasoline vapor, exhaust from cars and other vehicles, and even electric utilities! Thus, all of these processes can increase ozone in the air we breathe.",
        "air.ozone_image1_source": "Image source: Khan Academy",
        "air.ozone_image2_source": "Image source: Ozone Transport Commission",
        "air.ozone_cancer_title": "Ozone and Cancer",
        "air.ozone_cancer_p1": "Ozone has drastic effects on cancer outcomes. Lung cancer, kidney cancer, breast cancer, prostate cancer, and even brain cancer are just a few of the cancers that ozone can affect.",
        "air.ozone_cancer_p2": "It was found that a 10 µg/m³ (or 0.0051 ppm, the metric we use to measure ozone on this site) increase in ozone over a 3-day period can increase cancer mortality by 1%. This effect is especially pronounced during warmer times of the year.",
        "air.ozone_cancer_p3": "Ozone has such a strong effect on cancer mortality that ozone exposure had a significant effect on the likelihood of cancer death up to two days before the death.",
        "air.ozone_research_intro": "To learn more about lung cancer and ozone, check out some other relevant studies on:",
        "air.ozone_long_link_text": "Long-term ozone exposure",
        "air.ozone_short_link_text": "Short-term ozone exposure",
        "air.ozone_air_pollution_link_text": "Air pollution and lung cancer",
        "air.pm25_title": "PM2.5",
        "air.pm25_what_is": "What is PM2.5?",
        "air.pm25_lung_link_text": "One study",
        "air.pm25_p1": "PM2.5 stands for particulate matter 2.5. These are microscopic particles with diameters less than 2.5 µm, which is 30 times smaller than a human hair!",
        "air.pm25_p2": "These particles come from construction sites, sources of fire/smoke, unpaved roads, and chemical reactions in the atmosphere with other air pollutants, like SO2 and NO.",
        "air.pm25_image_source": "Image source: Environmental Protection Agency",
        "air.pm25_cancer_title": "PM2.5 and Cancer",
        "air.pm25_cancer_p1": "Increased PM2.5 values were found to independently predict a decrease in breast cancer survival. This pattern was tracked to have an increased hazard ratio (an indication of risk) by 1.144 per 1 µg/m³ increase of PM2.5 concentration. These effects are especially pronounced for older patients (65 years or older) as well as those in earlier stages of cancer diagnosis (stages I and II).",
        "air.pm25_cancer_p2": "Another study found that PM2.5 levels have a drastic effect on the incidence (aka development) of all gastrointestinal (GI) cancers. Specifically, the adjusted hazard ratio for a 1 standard deviation increase in PM2.5 mass is 1.367 for all GI cancers.",
        "air.pm25_cancer_p3": "The most studied cancer with relation to PM2.5 is lung cancer, as PM2.5 enters the body through the lungs.",
        "air.pm25_cancer_p4": "found that a 10 µg/m³ increase in PM2.5 related to a 7.95% increase in lung cancer mortality, with more significant effects on men and older folks (65 years or older).",
        "air.pm25_research_intro": "To learn more about lung cancer and PM2.5, check out some other relevant studies on:",
        "air.pm25_long_link_text": "Long-term PM2.5 exposure in U.S. adults",
        "air.pm25_cause_link_text": "How PM2.5 causes lung cancer",
        "air.pm25_male_link_text": "PM2.5 and male lung cancer",
        "air.pm25_ecology_link_text": "PM2.5 and lung cancer ecology",
        "air.did_you_know_title": "Did you know:",
        "air.did_you_know_text": "Areas with a lot of traffic are more likely to have ozone and PM2.5 air pollution.",
        "air.more_resources_title": "More resources",
        "air.traffic_image_source": "Image source: Centre for Economic Policy Research",
        "air.more_resources_p": "To get a more comprehensive understanding of your air quality and environmental health hazards, we encourage you to check out CalEnviroScreen 4.0. This is a tool put together by the California Office of Environmental Health Hazard Assessment. It is similar to this tool in that it allows you to look up information for your area, but with some different parameters as our tool focuses on cancer risk, rather than overall air health.",
        "air.calenviroscreen_link_text": "CalEnviroScreen 4.0",
        "resources.title": "Resources",
        "resources.subtitle": "Steps you can take to reduce your environmental cancer risk",
        "resources.intro": "We understand that much of the data provided in this tool mentions things that are out of your control, and a mere result of where you live. We know that completely moving to a new place with a healthier environment is completely unfeasible for many people (nor should a single website like this encourage you to make such a big decision). So here are some things you can control in light of your environmental cancer risk factors.",
        "resources.ndvi_title": "🌿 NDVI",
        "resources.ndvi_p1": "You may not be able to change the local vegetation around you, but that doesn't mean you can't expose yourself to more greenspaces. Making an effort to spend more time outdoors, especially in local parks or forests is a great idea, and can benefit your health. Community resources like hiking groups, run clubs, community gardens, or any other nature-friendly organization can be a great way to get yourself spending more time in greenspaces.",
        "resources.ndvi_p2": "You can also bring the greenspace to you! Getting some houseplants or starting a garden in your backyard can provide some of the mental benefits of being in nature, and can even help make the air around you cleaner! Additionally, growing fruits and vegetables at home is a cost-effective way to get clean, organic food while also exposing yourself to more greenery.",
        "resources.air_title": "💨 Air Quality",
        "resources.air_p1": "As much as air quality can seem pervasive, there are many things you can do to reduce your exposure to pollutants. One great way is to invest in high-quality, up-to-date air filters for your HVAC system at home, and/or portable air purification systems (i.e. HEPA filters). This can help prevent air pollutants from entering your home, and remove them out once they do. For more information about air filters, check out {link}.",
        "resources.air_p2": "Other ways to reduce air pollution exposure are to keep in mind the sources of air pollution, such as industrial processes or traffic. If you live off of a busy street, or by a construction site or other source of air pollution, it is a good idea to limit open windows in your home, especially during active hours. Moreover, if you find yourself sitting in traffic, closing the windows in your car can reduce exposure. If you do go outside into an area with heavy air pollution, wearing a face mask can help relieve any discomfort/smells, and reduce exposure.",
        "resources.epa_link_text": "EPA's Guide to Air Cleaners in the Home",
        "map.tooltip_input": "Input location",
        "map.tooltip_pixel": "Pixel center",
        "error.processing_coordinates": "Something went wrong while processing those coordinates",
        "back.to_home": "← Back to Home",
        "back.to_resources": "📋 Resources",
        "back.to_home_short": "← Back to Home",
    },
    "es": {
        "lang.select": "Seleccione Idioma",
        "lang.english": "English",
        "lang.spanish": "Español",
        "nav.home": "Inicio",
        "nav.ndvi": "NDVI",
        "nav.air_quality": "Calidad del aire",
        "nav.resources": "Recursos",
        "home.banner_title": "Buscador de Factores de Riesgo de Cáncer",
        "home.intro_1": "¡Bienvenido! Esta herramienta de búsqueda de factores de riesgo de cáncer está diseñada para ayudar a las personas que viven en California a mantenerse al tanto de su entorno y de cómo este puede influir en el riesgo de desarrollar cáncer y en sus posibles resultados.",
        "home.intro_2": "California es el estado más poblado del país y también uno de los más contaminados. Esto significa que muchas personas pueden ver afectada su salud por las condiciones ambientales de los lugares donde viven, trabajan y pasan su tiempo.",
        "home.intro_3": "Esta herramienta se basa en recursos existentes y utiliza información de herramientas de búsqueda por ubicación, como CalEnviroScreen y la Base de Datos de Agua Potable de EWG (Environmental Working Group), que ofrecen información sobre exposiciones ambientales. Sin embargo, estas herramientas están diseñadas principalmente para mostrar datos sobre distintos tipos de contaminantes y exposiciones. El objetivo del Buscador de Factores de Riesgo de Cáncer es ir un paso más allá: relacionar esa información con un resultado específico de salud, el cáncer.",
        "home.intro_4": "El cáncer es la segunda causa principal de muerte en Estados Unidos y una de las áreas de investigación médica que recibe más financiamiento de los Institutos Nacionales de la Salud (NIH). Como resultado, existe una gran cantidad de estudios científicos sobre esta enfermedad. Sin embargo, muchas personas no saben cómo los factores ambientales que las rodean pueden influir en su riesgo de desarrollar cáncer, aunque la ciencia moderna ha demostrado que estas conexiones existen.",
        "home.intro_5": "Por eso, esta herramienta busca ayudar a las personas a comprender mejor cómo podrían estar expuestas en su vida diaria a carcinógenos (sustancias que pueden causar cáncer) y ofrecer recursos que les permitan reducir o prevenir esas exposiciones. Además de explicar estos factores de riesgo, la herramienta proporciona información personalizada basada en la ubicación del usuario para mostrar cómo estos factores pueden estar presentes en su entorno y afectar su salud.",
        "home.search_intro": "Ingrese las coordenadas para ver información sobre la vegetación, la calidad del aire y los riesgos ambientales de cualquier lugar de California. Puede obtener las coordenadas de una dirección utilizando Google Maps.",
        "home.coord_label": "LATITUD, LONGITUD",
        "home.coord_placeholder": "Ej.: 34.05, -118.25",
        "ndvi.output_title": "Su resultado de NDVI",
        "ndvi.no_data": "No hay datos disponibles para esta ubicación.",
        "ndvi.percentile_text": "Como referencia, este valor es más alto que el de aproximadamente el {percentile}% de las áreas de California con un NDVI mayor que 0. El promedio estatal es {state_avg}.",
        "btn.whats_ndvi": "¿Qué es el NDVI?",
        "btn.learn_more_air": "Más información sobre la calidad del aire",
        "home.map_title": "🗺️ Mapa",
        "home.map_input_location": "Ubicación ingresada",
        "home.map_pixel_center": "Ubicación utilizada para el análisis",
        "home.map_legend_input": "Ubicación ingresada ({lat}, {lon})",
        "home.map_legend_pixel": "Ubicación utilizada para el análisis ({lat}, {lon})",
        "btn.resources": "📋 Recursos",
        "ndvi.title": "¿Qué es el NDVI?",
        "ndvi.subtitle": "Entendiendo el Índice de Vegetación de Diferencia Normalizada",
        "ndvi.no_result": "Ingrese las coordenadas en la página de Inicio para ver su resultado de NDVI aquí.",
        "ndvi.definition_title": "📖 Definición",
        "ndvi.definition_p1": "NDVI significa Índice de Vegetación de Diferencia Normalizada. Esta medida se utiliza para estimar cuánta vegetación (es decir, plantas vivas) hay en un área determinada. Los valores de NDVI se calculan a partir de imágenes satelitales que comparan la cantidad de luz que las plantas absorben con la cantidad de luz que reflejan.",
        "ndvi.image_source_eos": "Fuente de la imagen: EOS Data Analytics",
        "ndvi.values_title": "📊 Cómo interpretar los valores de NDVI",
        "ndvi.values_intro": "Los valores de NDVI van de −1 a 1:",
        "ndvi.negative_title": "Valores negativos",
        "ndvi.negative_desc": "Agua (cuerpos de agua, nubes o nieve)",
        "ndvi.zero_title": "Valores cercanos a cero",
        "ndvi.zero_desc": "Poca vegetación o suelo desnudo",
        "ndvi.positive_title": "Valores positivos",
        "ndvi.positive_desc": "Abundante vegetación saludable",
        "ndvi.cancer_title": "🔬 NDVI y la investigación sobre el cáncer",
        "ndvi.cancer_p1": "Diversos estudios han encontrado que los niveles más altos de NDVI se asocian con un menor riesgo de morir por cáncer. Esta relación se ha observado en varios tipos de cáncer, incluidos el cáncer de mama, de vejiga y de piel, pero ha sido especialmente notable en los casos de cáncer de próstata y de pulmón.",
        "ndvi.study_link_text": "En un estudio",
        "ndvi.cancer_p2": "los pacientes con cáncer de próstata que no se sometieron a cirugía tuvieron una mayor probabilidad de fallecer. Sin embargo, quienes vivían en áreas con valores medios de NDVI (0.217–0.278) presentaron un riesgo de mortalidad significativamente menor. Los pacientes que vivían en áreas con valores altos de NDVI (>0.278) mostraron un riesgo aún más bajo.",
        "ndvi.cancer_p3": "En general, los estudios han mostrado que los valores de NDVI superiores a 0.3 se relacionan con un menor riesgo de mortalidad por cáncer. Además, los aumentos en el NDVI a lo largo del tiempo (es decir, una mayor cantidad de vegetación) también se han asociado con mejores resultados de salud. Por ello, promover y proteger los espacios verdes, la vegetación y los entornos naturales puede ser beneficioso para la salud.",
        "ndvi.learn_more_title": "📚 Más información",
        "ndvi.learn_more_p": "Si desea obtener más información sobre la relación entre el NDVI y el cáncer, le recomendamos {link}, que resume gran parte de la investigación realizada sobre este tema. Es importante tener en cuenta que un valor más alto de NDVI no puede prevenir ni curar el cáncer por sí solo. Sin embargo, las investigaciones sugieren que vivir en áreas con más vegetación puede estar asociado con mejores resultados de salud.",
        "ndvi.learn_more_link_text": "consultar este estudio",
        "ndvi.image_source_earth": "Fuente de la imagen: earth.com",
        "air.title": "Calidad del aire",
        "air.subtitle": "Cómo la calidad del aire puede influir en el cáncer",
        "air.no_result": "Ingrese las coordenadas en la página de Inicio para ver su resultado de calidad del aire aquí.",
        "air.output_title": "Su resultado de calidad del aire",
        "air.ozone_label": "Ozono (máximo de 8 horas)",
        "air.pm25_label": "PM2.5 (promedio anual)",
        "air.percentile_word": "Percentil",
        "air.ozone_title": "Ozono",
        "air.ozone_what_is": "¿Qué es el ozono?",
        "air.ozone_p1": "El ozono, también conocido como O₃, es un gas altamente reactivo formado por tres átomos de oxígeno. En comparación, el oxígeno que normalmente respiramos es O₂, que está compuesto por dos átomos de oxígeno. Aunque pueda parecer que más oxígeno es algo positivo, el ozono es una molécula inestable que puede tener efectos perjudiciales para la salud.",
        "air.ozone_p2": "El ozono es un componente natural de la atmósfera superior. Sin embargo, el ozono a nivel del suelo, que es el que se encuentra en el aire que respiramos, no se produce de manera tan natural. Este tipo de ozono se forma cuando los óxidos de nitrógeno, los compuestos orgánicos volátiles y la luz solar reaccionan entre sí en la atmósfera. Los óxidos de nitrógeno y los compuestos orgánicos volátiles son contaminantes del aire que llegan a la atmósfera a través de diversas fuentes, como las emisiones de instalaciones industriales, los vapores de gasolina, los gases de escape de automóviles y otros vehículos, e incluso las empresas de servicios públicos que generan electricidad. Como resultado, todas estas fuentes pueden contribuir al aumento de los niveles de ozono en el aire que respiramos.",
        "air.ozone_image1_source": "Fuente de la imagen: Khan Academy",
        "air.ozone_image2_source": "Fuente de la imagen: Ozone Transport Commission",
        "air.ozone_cancer_title": "Ozono y cáncer",
        "air.ozone_cancer_p1": "El ozono puede tener efectos importantes en los resultados del cáncer. El cáncer de pulmón, de riñón, de mama, de próstata e incluso algunos tipos de cáncer cerebral son solo algunos de los cánceres que pueden verse afectados por la exposición al ozono.",
        "air.ozone_cancer_p2": "Se ha observado que un aumento de 10 µg/m³ de ozono (equivalente a 0.0051 ppm, la unidad que utilizamos para medir el ozono en este sitio) durante un período de tres días puede incrementar la mortalidad por cáncer en aproximadamente un 1 %. Este efecto es especialmente notable durante las épocas más cálidas del año.",
        "air.ozone_cancer_p3": "La relación entre el ozono y la mortalidad por cáncer es tan fuerte que la exposición al ozono se ha asociado con un aumento en el riesgo de muerte por cáncer incluso durante los dos días previos al fallecimiento.",
        "air.ozone_research_intro": "Para obtener más información sobre el cáncer de pulmón y el ozono, consulte algunos estudios relacionados sobre:",
        "air.ozone_long_link_text": "Exposición al ozono a largo plazo",
        "air.ozone_short_link_text": "Exposición al ozono a corto plazo",
        "air.ozone_air_pollution_link_text": "Contaminación del aire y cáncer de pulmón",
        "air.pm25_title": "PM2.5",
        "air.pm25_what_is": "¿Qué es el PM2.5?",
        "air.pm25_p1": "PM2.5 significa material particulado de 2.5 micrómetros. Se trata de partículas microscópicas con diámetros menores de 2.5 µm, lo que las hace aproximadamente 30 veces más pequeñas que el grosor de un cabello humano.",
        "air.pm25_p2": "Estas partículas pueden provenir de obras de construcción, incendios y humo, caminos sin pavimentar, y de reacciones químicas en la atmósfera que involucran otros contaminantes del aire, como el dióxido de azufre (SO₂) y el óxido nítrico (NO).",
        "air.pm25_image_source": "Fuente de la imagen: Environmental Protection Agency",
        "air.pm25_cancer_title": "PM2.5 y cáncer",
        "air.pm25_lung_link_text": "Un estudio",
        "air.pm25_cancer_p1": "Se ha encontrado que niveles más altos de PM2.5 pueden predecir de manera independiente una menor supervivencia en pacientes con cáncer de mama. Los investigadores observaron que por cada aumento de 1 µg/m³ en la concentración de PM2.5, el índice de riesgo (hazard ratio) aumentaba a 1.144, lo que indica un mayor riesgo de mortalidad. Estos efectos fueron especialmente marcados en pacientes mayores de 65 años y en aquellas personas diagnosticadas en etapas tempranas del cáncer (estadios I y II).",
        "air.pm25_cancer_p2": "Otro estudio encontró que los niveles de PM2.5 tienen un efecto importante sobre la incidencia (es decir, el desarrollo) de los cánceres gastrointestinales (GI). En particular, el índice de riesgo ajustado para un aumento de una desviación estándar en la concentración de PM2.5 fue de 1.367 para el conjunto de los cánceres gastrointestinales.",
        "air.pm25_cancer_p3": "El cáncer más estudiado en relación con el PM2.5 es el cáncer de pulmón, ya que estas partículas ingresan al organismo a través de los pulmones.",
        "air.pm25_cancer_p4": "encontró que un aumento de 10 µg/m³ en la concentración de PM2.5 se asoció con un incremento del 7.95 % en la mortalidad por cáncer de pulmón. Los efectos fueron aún más significativos en hombres y en personas mayores de 65 años.",
        "air.pm25_research_intro": "Para obtener más información sobre el cáncer de pulmón y el PM2.5, consulte algunos estudios relacionados sobre:",
        "air.pm25_long_link_text": "Exposición a largo plazo al PM2.5 en adultos de Estados Unidos",
        "air.pm25_cause_link_text": "Cómo el PM2.5 causa cáncer de pulmón",
        "air.pm25_male_link_text": "PM2.5 y el cáncer de pulmón en hombres",
        "air.pm25_ecology_link_text": "PM2.5 y cáncer de pulmón: estudios ecológicos",
        "air.did_you_know_title": "¿Sabía que...?",
        "air.did_you_know_text": "Las áreas con mucho tráfico vehicular suelen tener niveles más altos de contaminación del aire por ozono y PM2.5.",
        "air.more_resources_title": "Más recursos",
        "air.traffic_image_source": "Fuente de la imagen: Centre for Economic Policy Research",
        "air.more_resources_p": "Para obtener una visión más completa de la calidad del aire y de los riesgos ambientales para la salud en su comunidad, le recomendamos consultar CalEnviroScreen 4.0. Esta herramienta fue desarrollada por la Oficina de Evaluación de Riesgos para la Salud Ambiental de California (OEHHA). Al igual que esta herramienta, CalEnviroScreen le permite consultar información sobre su área. Sin embargo, ambas herramientas tienen enfoques diferentes: mientras que nuestro Buscador de Factores de Riesgo de Cáncer se centra en los riesgos relacionados con el cáncer, CalEnviroScreen está diseñado para evaluar una gama más amplia de factores relacionados con la salud ambiental.",
        "air.calenviroscreen_link_text": "CalEnviroScreen 4.0",
        "resources.title": "Recursos",
        "resources.subtitle": "Acciones que puede tomar para proteger su salud y reducir el riesgo de cáncer",
        "resources.intro": "Entendemos que gran parte de la información presentada en esta herramienta se refiere a factores que están fuera de su control y que, en muchos casos, dependen del lugar donde vive. También sabemos que mudarse a una zona con un entorno más saludable no es una opción realista para muchas personas. Además, una herramienta como esta no pretende sugerir decisiones tan importantes basándose únicamente en estos resultados. Por eso, a continuación encontrará algunas medidas que sí puede tomar para ayudar a reducir su exposición a factores ambientales relacionados con el riesgo de cáncer.",
        "resources.ndvi_title": "🌿 NDVI",
        "resources.ndvi_p1": "Es posible que no pueda cambiar la cantidad de vegetación que existe en su vecindario, pero eso no significa que no pueda pasar más tiempo en espacios verdes. Hacer un esfuerzo por pasar más tiempo al aire libre, especialmente en parques, senderos naturales o bosques cercanos, puede beneficiar su salud. Los recursos comunitarios, como grupos de senderismo, clubes de corredores, huertos comunitarios u otras organizaciones relacionadas con la naturaleza, también pueden ser una excelente manera de pasar más tiempo en entornos con vegetación.",
        "resources.ndvi_p2": "¡También puede acercar los espacios verdes a su propio hogar! Tener plantas de interior o crear un jardín en su patio puede ofrecer algunos de los beneficios para el bienestar que proporciona el contacto con la naturaleza. Además, las plantas pueden ayudar a mejorar la calidad del aire en su entorno. Cultivar frutas y verduras en casa también puede ser una forma económica de acceder a alimentos frescos y de calidad, al mismo tiempo que incorpora más vegetación a su vida diaria.",
        "resources.air_title": "💨 Calidad del aire",
        "resources.air_p1": "Aunque la contaminación del aire puede parecer difícil de evitar, existen muchas medidas que puede tomar para reducir su exposición a los contaminantes. Una de las más efectivas es utilizar filtros de aire modernos y de alta calidad en el sistema de calefacción y aire acondicionado de su hogar (HVAC) y/o emplear purificadores de aire portátiles, como los que utilizan filtros HEPA. Estos dispositivos pueden ayudar a evitar que los contaminantes entren en su hogar y a eliminarlos del aire interior. Para obtener más información sobre los filtros de aire, consulte {link}.",
        "resources.air_p2": "Otra forma de reducir la exposición a la contaminación del aire es prestar atención a las fuentes de contaminación cercanas, como el tráfico intenso, las obras de construcción o las instalaciones industriales. Si vive cerca de una calle con mucho tráfico o de otra fuente importante de contaminación, es recomendable mantener las ventanas cerradas durante los períodos de mayor actividad. Además, si pasa tiempo en el tráfico, cerrar las ventanas de su vehículo puede ayudar a reducir la exposición a los contaminantes. Si necesita estar al aire libre en una zona con altos niveles de contaminación, usar una mascarilla puede ayudar a reducir la exposición y aliviar algunas molestias causadas por la mala calidad del aire, como los olores o la irritación.",
        "resources.epa_link_text": "Guía de Purificadores de Aire para el Hogar de la EPA",
        "map.tooltip_input": "Ubicación ingresada",
        "map.tooltip_pixel": "Ubicación utilizada para el análisis",
        "error.processing_coordinates": "Ocurrió un error al procesar las coordenadas.",
        "back.to_home": "← Volver al inicio",
        "back.to_resources": "📋 Recursos",
        "back.to_home_short": "← Volver al inicio",
    },
}

def t(key: str, **kwargs) -> str:
    lang = st.session_state.get("lang", "en")
    value = TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)
    if kwargs:
        return value.format(**kwargs)
    return value

def link(url: str, label: str, style: str = "") -> str:
    style_attr = f' style="{style}"' if style else ""
    return f'<a href="{url}" target="_blank" rel="noopener noreferrer"{style_attr}>{label}</a>'

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --sage:    #4a7c59;
    --sage-lt: #e8f0eb;
    --sky:     #3a7ca5;
    --earth:   #8b6f47;
    --sand:    #f7f3ed;
    --white:   #ffffff;
    --ink:     #1e2d1f;
    --muted:   #6b7c6d;
    --border:  #d8e4d9;
    --radius:  12px;
    --shadow:  0 2px 12px rgba(74,124,89,0.10);
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--sand) !important;
    font-family: 'DM Sans', sans-serif;
    color: var(--ink);
}

#MainMenu, footer, header { visibility: hidden; }

[data-testid="stSidebar"] {
    background: var(--white) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * {
    font-family: 'DM Sans', sans-serif !important;
}

[data-testid="stSidebarNav"] a {
    border-radius: 8px !important;
    font-size: 0.9rem !important;
    font-weight: 500 !important;
    color: var(--muted) !important;
    padding: 0.45rem 0.75rem !important;
    transition: background 0.15s, color 0.15s;
}
[data-testid="stSidebarNav"] a:hover {
    background: var(--sage-lt) !important;
    color: var(--sage) !important;
}
[data-testid="stSidebarNav"] [aria-current="page"] a,
[data-testid="stSidebarNav"] a[aria-selected="true"] {
    background: var(--sage-lt) !important;
    color: var(--sage) !important;
    font-weight: 600 !important;
}

[data-testid="stSidebarCollapseButton"] button,
[data-testid="stSidebarUserContent"] ~ div button,
button[kind="header"] {
    background: var(--white) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--sage) !important;
    width: 32px !important;
    height: 32px !important;
    padding: 0 !important;
    box-shadow: var(--shadow) !important;
    transition: background 0.15s !important;
}
[data-testid="stSidebarCollapseButton"] button:hover,
button[kind="header"]:hover {
    background: var(--sage-lt) !important;
}

[data-testid="collapsedControl"] {
    background: var(--white) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    box-shadow: var(--shadow) !important;
}
[data-testid="collapsedControl"] button {
    color: var(--sage) !important;
}

[data-testid="stMainBlockContainer"] {
    padding: 0 2rem 3rem 2rem !important;
    max-width: 860px;
}

.page-header {
    background: linear-gradient(135deg, #2d5a3d 0%, #3a7ca5 100%);
    border-radius: var(--radius);
    padding: 2rem 2.25rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.page-header::before {
    content: '';
    position: absolute;
    top: -40px; right: -40px;
    width: 180px; height: 180px;
    border-radius: 50%;
    background: rgba(255,255,255,0.06);
}
.page-header::after {
    content: '';
    position: absolute;
    bottom: -30px; left: 30%;
    width: 120px; height: 120px;
    border-radius: 50%;
    background: rgba(255,255,255,0.04);
}
.page-header h1 {
    font-family: 'DM Serif Display', serif;
    font-size: 1.9rem;
    color: #ffffff;
    margin: 0 0 0.3rem 0;
    letter-spacing: -0.02em;
}
.page-header p {
    font-size: 0.875rem;
    color: rgba(255,255,255,0.78);
    margin: 0;
    font-weight: 300;
}

.card {
    background: var(--white);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.5rem 1.75rem;
    margin-bottom: 1.25rem;
    box-shadow: var(--shadow);
}
.card-title {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 1rem;
}

.metrics-row { display: flex; gap: 1rem; flex-wrap: wrap; }
.metric-chip {
    flex: 1;
    min-width: 160px;
    background: var(--sand);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1rem 1.25rem;
}
.metric-chip .metric-label {
    font-size: 0.72rem;
    font-weight: 600;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.07em;
    margin-bottom: 0.4rem;
}
.metric-chip .metric-value {
    font-size: 1.6rem;
    font-weight: 600;
    color: var(--ink);
    line-height: 1;
}
.metric-chip .metric-pctl {
    font-size: 0.78rem;
    color: var(--muted);
    margin-top: 0.3rem;
}
.chip-sky   { border-left: 4px solid var(--sky); }
.chip-earth { border-left: 4px solid var(--earth); }

.ndvi-score {
    font-family: 'DM Serif Display', serif;
    font-size: 3.2rem;
    color: var(--sage);
    line-height: 1;
    margin: 0.25rem 0 0.25rem 0;
}
.ndvi-sub {
    color: #6b7c6d;
    font-size: 0.82rem;
    margin: 0.4rem 0 0 0;
}
.ndvi-na {
    font-size: 1.2rem;
    color: var(--muted);
    font-style: italic;
}

.legend-row {
    display: flex;
    gap: 1.5rem;
    margin-bottom: 0.75rem;
    font-size: 0.82rem;
    color: var(--muted);
}
.legend-dot {
    display: inline-block;
    width: 10px; height: 10px;
    border-radius: 50%;
    margin-right: 5px;
    vertical-align: middle;
}

[data-testid="stTextInput"] input {
    border-radius: 8px !important;
    border: 1px solid var(--border) !important;
    background: var(--white) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important;
    padding: 0.55rem 0.85rem !important;
    color: var(--ink) !important;
    box-shadow: none !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: var(--sage) !important;
    box-shadow: 0 0 0 3px rgba(74,124,89,0.12) !important;
}
[data-testid="stTextInput"] label {
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    color: var(--muted) !important;
    text-transform: uppercase !important;
    letter-spacing: 0.07em !important;
}

[data-testid="stButton"] button {
    background: var(--sage) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    padding: 0.5rem 1.25rem !important;
    transition: background 0.15s, transform 0.1s !important;
    box-shadow: 0 2px 8px rgba(74,124,89,0.2) !important;
}
[data-testid="stButton"] button:hover {
    background: #3a6347 !important;
    transform: translateY(-1px) !important;
}

[data-testid="stAlert"] {
    border-radius: var(--radius) !important;
    font-family: 'DM Sans', sans-serif !important;
}

.img-caption {
    font-size: 0.75rem;
    color: var(--muted);
    text-align: center;
    margin-top: 0.4rem;
    margin-bottom: 0.5rem;
}
.img-caption a {
    color: var(--muted);
    text-decoration: underline;
    text-underline-offset: 2px;
}
.img-caption a:hover {
    color: var(--sage);
}

.did-you-know {
    background: var(--sage-lt);
    border: 1px solid var(--border);
    border-left: 4px solid var(--sage);
    border-radius: 8px;
    padding: 0.85rem 1.1rem;
    margin-top: 0.75rem;
    font-size: 0.9rem;
    color: var(--ink);
    line-height: 1.6;
}
</style>
""",
    unsafe_allow_html=True,
)


def download_tif_if_needed():
    if os.path.exists(TIF_PATH):
        return TIF_PATH

    from huggingface_hub import hf_hub_download

    downloaded_path = hf_hub_download(
        repo_id="jordanl2/ndvi-data",
        filename="NDVI_california.tif",
        repo_type="dataset",
        local_dir="/tmp",
        token=os.getenv("HF_TOKEN"),
    )
    return downloaded_path


@st.cache_resource
def open_raster():
    tif_path = download_tif_if_needed()
    return rasterio.open(tif_path)


@st.cache_data
def load_calenviro(path):
    return pd.read_excel(path, engine="openpyxl")


@st.cache_resource
def compute_ndvi_stats():
    """
    Build a compact summary of the raster:
    - histogram counts for percentile estimates
    - total sum and count for mean
    This avoids holding all NDVI values in memory.
    """
    tif_path = download_tif_if_needed()

    if os.path.exists(NDVI_STATS_PATH):
        data = np.load(NDVI_STATS_PATH)
        return (
            data["edges"],
            data["counts"],
            float(data["total_sum"]),
            int(data["total_count"]),
        )

    src = rasterio.open(tif_path)

    counts = np.zeros(len(NDVI_BINS) - 1, dtype=np.int64)
    total_sum = 0.0
    total_count = 0

    for _, window in src.block_windows(1):
        block = src.read(1, window=window, masked=True)
        vals = block.compressed()
        vals = vals[np.isfinite(vals) & (vals > 0)]

        if vals.size:
            hist, _ = np.histogram(vals, bins=NDVI_BINS)
            counts += hist.astype(np.int64)
            total_sum += float(vals.sum())
            total_count += int(vals.size)

    np.savez(
        NDVI_STATS_PATH,
        edges=NDVI_BINS,
        counts=counts,
        total_sum=total_sum,
        total_count=total_count,
    )

    return NDVI_BINS, counts, total_sum, total_count


def ndvi_percentile(ndvi_value: float) -> float:
    edges, counts, _, total_count = compute_ndvi_stats()

    if total_count == 0 or ndvi_value is None:
        return 0.0

    if ndvi_value <= 0:
        return 0.0

    idx = np.searchsorted(edges, ndvi_value, side="right") - 1
    idx = max(0, min(idx, len(counts) - 1))

    cum_before = int(counts[:idx].sum())
    bin_left = edges[idx]
    bin_right = edges[idx + 1]
    bin_count = int(counts[idx])

    if bin_count == 0:
        approx_rank = cum_before
    else:
        frac_in_bin = (ndvi_value - bin_left) / (bin_right - bin_left)
        frac_in_bin = max(0.0, min(1.0, frac_in_bin))
        approx_rank = cum_before + (bin_count * frac_in_bin)

    return round((approx_rank / total_count) * 100, 1)


def ndvi_state_average() -> float:
    _, _, total_sum, total_count = compute_ndvi_stats()
    if total_count == 0:
        return float("nan")
    return round(total_sum / total_count, 3)


def find_nearest_tract(df, lat, lon):
    temp = df.copy()
    temp["distance"] = (temp["Latitude"] - lat) ** 2 + (temp["Longitude"] - lon) ** 2
    return temp.loc[temp["distance"].idxmin()]


def fmt3(value):
    if pd.isna(value):
        return "N/A"
    try:
        return f"{float(value):.3g}"
    except Exception:
        return str(value)


def compute_location_data(lat: float, lon: float):
    calenv_df = load_calenviro(CALENV_PATH)
    src = open_raster()
    to_utm = Transformer.from_crs("EPSG:4326", src.crs, always_xy=True)
    to_wgs84 = Transformer.from_crs(src.crs, "EPSG:4326", always_xy=True)

    x, y = to_utm.transform(lon, lat)
    sampled = next(src.sample([(x, y)], masked=True))[0]

    row, col = src.index(x, y)
    pixel_x, pixel_y = src.xy(row, col)
    pixel_lon, pixel_lat = to_wgs84.transform(pixel_x, pixel_y)

    ndvi_value = None
    ndvi_pctl = None
    if not getattr(sampled, "mask", False):
        ndvi_value = float(sampled)
        if ndvi_value > 0:
            ndvi_pctl = ndvi_percentile(ndvi_value)

    tract = find_nearest_tract(calenv_df, lat, lon)
    ozone = fmt3(tract["Ozone"])
    ozone_pctl = fmt3(tract["Ozone Pctl"])
    pm25 = fmt3(tract["PM2.5"])
    pm25_pctl = fmt3(tract["PM2.5 Pctl"])

    return {
        "lat": lat,
        "lon": lon,
        "pixel_lat": pixel_lat,
        "pixel_lon": pixel_lon,
        "ndvi_value": ndvi_value,
        "ndvi_pctl": ndvi_pctl,
        "ozone": ozone,
        "ozone_pctl": ozone_pctl,
        "pm25": pm25,
        "pm25_pctl": pm25_pctl,
    }


def store_last_result(data: dict):
    st.session_state["last_result"] = data
    st.session_state["last_latlon_text"] = f"{data['lat']:.5f}, {data['lon']:.5f}"


def render_language_picker():
    st.markdown(
        f"""
        <div class="page-header">
            <h1>{APP_TITLE}</h1>
            <p>{APP_SUBTITLE}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <div class="card">
            <div class="card-title">{t("lang.select")}</div>
            <p style="font-size:0.95rem;line-height:1.7;color:#1e2d1f;margin:0 0 1rem 0;">Choose the language for the site.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns(2)
    with c1:
        if st.button(t("lang.english"), key="choose_english"):
            st.session_state["lang"] = "en"
            st.rerun()
    with c2:
        if st.button(t("lang.spanish"), key="choose_spanish"):
            st.session_state["lang"] = "es"
            st.rerun()


def render_banner(title: str, desc: str = ""):
    desc_html = f"<p>{desc}</p>" if desc else ""
    st.markdown(
        '<div class="page-header">'
        f"<h1>{title}</h1>"
        f"{desc_html}"
        "</div>",
        unsafe_allow_html=True,
    )


def render_ndvi_output_card(data: dict):
    ndvi_value = data.get("ndvi_value")
    ndvi_pctl = data.get("ndvi_pctl")
    if ndvi_value is None:
        ndvi_inner = f'<div class="ndvi-na">{t("ndvi.no_data")}</div>'
    else:
        ndvi_inner = f'<div class="ndvi-score">{fmt3(ndvi_value)}</div>'
        if ndvi_pctl is not None:
            state_avg = ndvi_state_average()
            ndvi_inner += (
                '<div class="ndvi-sub">'
                + t("ndvi.percentile_text", percentile=ndvi_pctl, state_avg=state_avg)
                + "</div>"
            )
    st.markdown(
        '<div class="card">'
        f'<div class="card-title">{t("ndvi.output_title")}</div>'
        f"{ndvi_inner}"
        "</div>",
        unsafe_allow_html=True,
    )


def render_air_quality_output_card(data: dict):
    st.markdown(
        '<div class="card">'
        f'<div class="card-title">{t("air.output_title")}</div>'
        '<div class="metrics-row">'
        '<div class="metric-chip chip-sky">'
        f'<div class="metric-label">{t("air.ozone_label")}</div>'
        f'<div class="metric-value">{data["ozone"]}</div>'
        f'<div class="metric-pctl">ppm &nbsp;&middot;&nbsp; {data["ozone_pctl"]} {t("air.percentile_word")}</div>'
        '</div>'
        '<div class="metric-chip chip-earth">'
        f'<div class="metric-label">{t("air.pm25_label")}</div>'
        f'<div class="metric-value">{data["pm25"]}</div>'
        f'<div class="metric-pctl">&#181;g/m&#179; &nbsp;&middot;&nbsp; {data["pm25_pctl"]} {t("air.percentile_word")}</div>'
        '</div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )


def back_button_home(key: str):
    if st.button(t("back.to_home"), key=key):
        st.switch_page(home_page)


def resources_button(key: str):
    if st.button(t("btn.resources"), key=key):
        st.switch_page(resources_page)


def render_home():
    render_banner(title=t("home.banner_title"))

    st.markdown(
        '<div class="card">'
        f'<p style="font-size:0.95rem;line-height:1.75;color:#1e2d1f;margin:0 0 1rem 0;">{t("home.intro_1")}</p>'
        f'<p style="font-size:0.95rem;line-height:1.75;color:#1e2d1f;margin:0 0 1rem 0;">{t("home.intro_2")}</p>'
        f'<p style="font-size:0.95rem;line-height:1.75;color:#1e2d1f;margin:0;">{t("home.intro_3")} {t("home.intro_4")}</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<p style="font-size:0.875rem;color:#6b7c6d;margin:0 0 0.5rem 0;">{t("home.search_intro")}</p>',
        unsafe_allow_html=True,
    )

    if "last_latlon_text" in st.session_state and "home_latlon_input" not in st.session_state:
        st.session_state["home_latlon_input"] = st.session_state["last_latlon_text"]

    latlon = st.text_input(
        t("home.coord_label"),
        placeholder=t("home.coord_placeholder"),
        key="home_latlon_input",
    )
    st.caption(t("home.coord_placeholder"))

    if latlon:
        try:
            lat_str, lon_str = latlon.split(",")
            lat = float(lat_str.strip())
            lon = float(lon_str.strip())

            data = compute_location_data(lat, lon)
            store_last_result(data)

            render_ndvi_output_card(data)

            if st.button(t("btn.whats_ndvi"), key="whats_ndvi_btn"):
                st.switch_page(ndvi_page)

            render_air_quality_output_card(data)

            if st.button(t("btn.learn_more_air"), key="learn_more_air_quality_btn"):
                st.switch_page(air_quality_page)

            input_lat = f"{data['lat']:.5f}"
            input_lon = f"{data['lon']:.5f}"
            pixel_lat = f"{data['pixel_lat']:.5f}"
            pixel_lon = f"{data['pixel_lon']:.5f}"

            st.markdown(
                '<div class="card">'
                f'<div class="card-title">{t("home.map_title")}</div>'
                '<div class="legend-row">'
                '<span><span class="legend-dot" style="background:#3a7ca5;"></span>'
                f'{t("home.map_legend_input").format(lat=input_lat, lon=input_lon)}</span>'
                '<span><span class="legend-dot" style="background:#c0392b;"></span>'
                f'{t("home.map_legend_pixel").format(lat=pixel_lat, lon=pixel_lon)}</span>'
                '</div>'
                '</div>',
                unsafe_allow_html=True,
            )

            map_df = pd.DataFrame([
                {"lat": data["lat"], "lon": data["lon"], "point_type": t("map.tooltip_input")},
                {"lat": data["pixel_lat"], "lon": data["pixel_lon"], "point_type": t("map.tooltip_pixel")},
            ])

            st.pydeck_chart(
                pdk.Deck(
                    layers=[
                        pdk.Layer(
                            "ScatterplotLayer",
                            data=map_df[map_df["point_type"] == t("map.tooltip_input")],
                            get_position="[lon, lat]",
                            get_fill_color=[58, 124, 165, 210],
                            get_radius=80,
                            pickable=True,
                        ),
                        pdk.Layer(
                            "ScatterplotLayer",
                            data=map_df[map_df["point_type"] == t("map.tooltip_pixel")],
                            get_position="[lon, lat]",
                            get_fill_color=[192, 57, 43, 210],
                            get_radius=80,
                            pickable=True,
                        ),
                    ],
                    initial_view_state=pdk.ViewState(
                        latitude=(data["lat"] + data["pixel_lat"]) / 2,
                        longitude=(data["lon"] + data["pixel_lon"]) / 2,
                        zoom=11,
                        pitch=0,
                    ),
                    tooltip={"text": "{point_type}\n({lat}, {lon})"},
                    map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
                )
            )

        except Exception as e:
            st.error(t("error.processing_coordinates"))
            st.exception(e)
    
    resources_button("resources_from_home_btn")

def render_ndvi():
    render_banner(
        title=t("ndvi.title"),
        desc=t("ndvi.subtitle"),
    )

    if "last_result" in st.session_state:
        render_ndvi_output_card(st.session_state["last_result"])
    else:
        st.info(t("ndvi.no_result"))

    st.markdown(
        '<div class="card">'
        f'<div class="card-title">{t("ndvi.definition_title")}</div>'
        f'<p style="font-size:0.95rem;line-height:1.7;color:#1e2d1f;margin:0;">{t("ndvi.definition_p1")}</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.image("NDVI.webp", use_container_width=True)
    st.markdown(
        f'<p class="img-caption">{link("https://eos.com/blog/normalized-difference-vegetation-index-or-ndvi/", t("ndvi.image_source_eos"))}</p>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="card">'
        f'<div class="card-title">{t("ndvi.values_title")}</div>'
        f'<p style="font-size:0.88rem;color:#6b7c6d;margin:0 0 0.85rem 0;">{t("ndvi.values_intro")}</p>'
        '<div style="display:flex;flex-direction:column;gap:0.6rem;">'
        '<div style="display:flex;align-items:flex-start;gap:0.85rem;padding:0.75rem 1rem;background:#e6f1f8;border-radius:8px;border-left:4px solid #3a7ca5;">'
        '<span style="font-size:1.1rem;">💧</span>'
        '<div><div style="font-size:0.78rem;font-weight:600;color:#3a7ca5;text-transform:uppercase;letter-spacing:0.07em;margin-bottom:0.2rem;">'
        f'{t("ndvi.negative_title")}</div><div style="font-size:0.9rem;color:#1e2d1f;">{t("ndvi.negative_desc")}</div></div></div>'
        '<div style="display:flex;align-items:flex-start;gap:0.85rem;padding:0.75rem 1rem;background:#f5efe6;border-radius:8px;border-left:4px solid #8b6f47;">'
        '<span style="font-size:1.1rem;">🏜️</span>'
        '<div><div style="font-size:0.78rem;font-weight:600;color:#8b6f47;text-transform:uppercase;letter-spacing:0.07em;margin-bottom:0.2rem;">'
        f'{t("ndvi.zero_title")}</div><div style="font-size:0.9rem;color:#1e2d1f;">{t("ndvi.zero_desc")}</div></div></div>'
        '<div style="display:flex;align-items:flex-start;gap:0.85rem;padding:0.75rem 1rem;background:#e8f0eb;border-radius:8px;border-left:4px solid #4a7c59;">'
        '<span style="font-size:1.1rem;">🌿</span>'
        '<div><div style="font-size:0.78rem;font-weight:600;color:#4a7c59;text-transform:uppercase;letter-spacing:0.07em;margin-bottom:0.2rem;">'
        f'{t("ndvi.positive_title")}</div><div style="font-size:0.9rem;color:#1e2d1f;">{t("ndvi.positive_desc")}</div></div></div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    study_link = link(
        "https://www.sciencedirect.com/science/article/pii/S016041202500563X?ref=pdf_download&fr=RR-2&rr=9f0333456b4c2ab4",
        t("ndvi.study_link_text"),
        "color:#4a7c59;font-weight:600;text-decoration:underline;text-underline-offset:3px;",
    )
    st.markdown(
        '<div class="card">'
        f'<div class="card-title">{t("ndvi.cancer_title")}</div>'
        f'<p style="font-size:0.95rem;line-height:1.7;color:#1e2d1f;margin:0 0 1rem 0;">{t("ndvi.cancer_p1")}</p>'
        f'<p style="font-size:0.95rem;line-height:1.7;color:#1e2d1f;margin:0 0 1rem 0;">{study_link}, {t("ndvi.cancer_p2")}</p>'
        f'<p style="font-size:0.95rem;line-height:1.7;color:#1e2d1f;margin:0;">{t("ndvi.cancer_p3")}</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.image("Wellness.jpeg", use_container_width=True)
    st.markdown(
        f'<p class="img-caption">{link("https://www.earth.com/news/nature-boosts-health-well-being/", t("ndvi.image_source_earth"))}</p>',
        unsafe_allow_html=True,
    )

    learn_link = link(
        "https://pubmed.ncbi.nlm.nih.gov/37474858/",
        t("ndvi.learn_more_link_text"),
        "color:#4a7c59;font-weight:600;text-decoration:underline;text-underline-offset:3px;",
    )
    st.markdown(
        '<div class="card" style="background:#e8f0eb;border-color:#4a7c59;">'
        f'<div class="card-title" style="color:#4a7c59;">{t("ndvi.learn_more_title")}</div>'
        f'<p style="font-size:0.95rem;line-height:1.7;color:#1e2d1f;margin:0;">{t("ndvi.learn_more_p").format(link=learn_link)}</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    back_button_home("back_to_home_btn")
    resources_button("resources_from_ndvi_btn")


def render_air_quality():
    render_banner(
        title=t("air.title"),
        desc=t("air.subtitle"),
    )

    if "last_result" in st.session_state:
        render_air_quality_output_card(st.session_state["last_result"])
    else:
        st.info(t("air.no_result"))

    st.markdown(
        '<div class="card">'
        f'<div class="card-title">{t("air.ozone_title")}</div>'
        f'<p style="font-size:0.95rem;line-height:1.7;color:#1e2d1f;margin:0;"><strong>{t("air.ozone_what_is")}</strong><br>{t("air.ozone_p1")}<br><br>{t("air.ozone_p2")}</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.image("Ozone1.png", use_container_width=True)
    st.markdown(
        f'<p class="img-caption">{link("https://www.khanacademy.org/science/ap-college-environmental-science/x0b0e430a38ebd23f:gl", t("air.ozone_image1_source"))}</p>',
        unsafe_allow_html=True,
    )
    st.image("Ozone2.png", use_container_width=True)
    st.markdown(
        f'<p class="img-caption">{link("https://otcair.org/about-ozone", t("air.ozone_image2_source"))}</p>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="card">'
        f'<div class="card-title">{t("air.ozone_cancer_title")}</div>'
        f'<p style="font-size:0.95rem;line-height:1.7;color:#1e2d1f;margin:0;">{t("air.ozone_cancer_p1")}<br><br>{t("air.ozone_cancer_p2")}<br><br>{t("air.ozone_cancer_p3")}<br><br>{t("air.ozone_research_intro")}<br>'
        f'&bull; {link("https://www.nature.com/articles/s41370-019-0135-4", t("air.ozone_long_link_text"), "color:#4a7c59;font-weight:600;text-decoration:underline;text-underline-offset:3px;")}<br>'
        f'&bull; {link("https://pubmed.ncbi.nlm.nih.gov/38985095/", t("air.ozone_short_link_text"), "color:#4a7c59;font-weight:600;text-decoration:underline;text-underline-offset:3px;")}<br>'
        f'&bull; {link("https://ascopost.com/news/january-2026/associations-found-between-air-pollutants-and-lung-cancer-subtypes/", t("air.ozone_air_pollution_link_text"), "color:#4a7c59;font-weight:600;text-decoration:underline;text-underline-offset:3px;")}'
        '</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="card">'
        f'<div class="card-title">{t("air.pm25_title")}</div>'
        f'<p style="font-size:0.95rem;line-height:1.7;color:#1e2d1f;margin:0;"><strong>{t("air.pm25_what_is")}</strong><br>{t("air.pm25_p1")}<br>{t("air.pm25_p2")}</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.image("PM2.5.jpg", use_container_width=True)
    st.markdown(
        f'<p class="img-caption">{link("https://www.epa.gov/pm-pollution/particulate-matter-pm-basics", t("air.pm25_image_source"))}</p>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="card">'
        f'<div class="card-title">{t("air.pm25_cancer_title")}</div>'
        f'<p style="font-size:0.95rem;line-height:1.7;color:#1e2d1f;margin:0;">'
        f'{t("air.pm25_cancer_p1")}<br><br>'
        f'{t("air.pm25_cancer_p2")}<br><br>'
        f'{t("air.pm25_cancer_p3")} '
        f'{link("https://oce-ovid-com.libproxy1.usc.edu/article/00008469-202211000-00006/PDF", t("air.pm25_lung_link_text"), "color:#4a7c59;font-weight:600;text-decoration:underline;text-underline-offset:3px;")} '
        f'{t("air.pm25_cancer_p4")}<br><br>'
        f'{t("air.pm25_research_intro")}<br>'
        f'&bull; {link("https://pmc.ncbi.nlm.nih.gov/articles/PMC6915823/pdf/kwx166.pdf", t("air.pm25_long_link_text"), "color:#4a7c59;font-weight:600;text-decoration:underline;text-underline-offset:3px;")}<br>'
        f'&bull; {link("https://pubmed.ncbi.nlm.nih.gov/28846189/", t("air.pm25_cause_link_text"), "color:#4a7c59;font-weight:600;text-decoration:underline;text-underline-offset:3px;")}<br>'
        f'&bull; {link("https://pubmed.ncbi.nlm.nih.gov/28724219/", t("air.pm25_male_link_text"), "color:#4a7c59;font-weight:600;text-decoration:underline;text-underline-offset:3px;")}<br>'
        f'&bull; {link("https://www.proquest.com/docview/3307473046?accountid=14749&parentSessionId=ebTcDAjx0wcSqNJ6ZPbbZyurTyde0SdRnOJayaC237A%3D&pq-origsite=primo&sourcetype=Scholarly%20Journals", t("air.pm25_ecology_link_text"), "color:#4a7c59;font-weight:600;text-decoration:underline;text-underline-offset:3px;")}'
        '</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.image("Traffic.webp", use_container_width=True)
    st.markdown(
        f'<p class="img-caption">{link("https://cepr.org/voxeu/columns/road-traffic-flow-and-air-pollution-concentrations-evidence-japan", t("air.traffic_image_source"))}</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="did-you-know"><strong>{t("air.did_you_know_title")}</strong> {t("air.did_you_know_text")}</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="card" style="background:#e8f0eb;border-color:#4a7c59;margin-top:1.25rem;">'
        f'<div class="card-title" style="color:#4a7c59;">{t("air.more_resources_title")}</div>'
        f'<p style="font-size:0.95rem;line-height:1.7;color:#1e2d1f;margin:0;">{t("air.more_resources_p").replace("CalEnviroScreen 4.0", link("https://oehha.ca.gov/calenviroscreen/report/calenviroscreen-40", t("air.calenviroscreen_link_text"), "color:#4a7c59;font-weight:600;text-decoration:underline;text-underline-offset:3px;"))}</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    back_button_home("back_to_home_air_quality_btn")
    resources_button("resources_from_air_quality_btn")


def render_resources():
    render_banner(
        title=t("resources.title"),
        desc=t("resources.subtitle"),
    )

    st.markdown(
        '<div class="card">'
        f'<p style="font-size:0.95rem;line-height:1.75;color:#1e2d1f;margin:0;">{t("resources.intro")}</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="card">'
        f'<div class="card-title">{t("resources.ndvi_title")}</div>'
        f'<p style="font-size:0.95rem;line-height:1.75;color:#1e2d1f;margin:0 0 1rem 0;">{t("resources.ndvi_p1")}</p>'
        f'<p style="font-size:0.95rem;line-height:1.75;color:#1e2d1f;margin:0;">{t("resources.ndvi_p2")}</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    epa_link = link(
        "https://www.epa.gov/indoor-air-quality-iaq/guide-air-cleaners-home",
        t("resources.epa_link_text"),
        "color:#4a7c59;font-weight:600;text-decoration:underline;text-underline-offset:3px;",
    )
    st.markdown(
        '<div class="card">'
        f'<div class="card-title">{t("resources.air_title")}</div>'
        f'<p style="font-size:0.95rem;line-height:1.75;color:#1e2d1f;margin:0 0 1rem 0;">{t("resources.air_p1").format(link=epa_link)}</p>'
        f'<p style="font-size:0.95rem;line-height:1.75;color:#1e2d1f;margin:0;">{t("resources.air_p2")}</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    back_button_home("back_to_home_resources_btn")


st.session_state.setdefault("lang", None)

if st.session_state["lang"] is None:
    render_language_picker()
    st.stop()

home_page = st.Page(render_home, title=t("nav.home"), default=True)
ndvi_page = st.Page(render_ndvi, title=t("nav.ndvi"))
air_quality_page = st.Page(render_air_quality, title=t("nav.air_quality"))
resources_page = st.Page(render_resources, title=t("nav.resources"))

pg = st.navigation([home_page, ndvi_page, air_quality_page, resources_page])
pg.run()
