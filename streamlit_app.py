import streamlit as st
import pandas as pd
import plotly.express as px
import base64
import os
import requests

# Configuración inicial
st.set_page_config(page_title="Dashboard del Proyecto", layout="wide", page_icon="📅")

# Inicializar estado de sesión para la navegación
if 'pagina_actual' not in st.session_state:
    st.session_state.pagina_actual = "Gantt"

def cambiar_pagina(nueva_pagina):
    st.session_state.pagina_actual = nueva_pagina

# ==========================================
# CARGA DE DATOS DESDE CSV
# ==========================================
@st.cache_data
def cargar_datos():
    archivo_csv = "cronograma.csv"
    if os.path.exists(archivo_csv):
        df = pd.read_csv(archivo_csv)
        # Convertir columnas de fecha a formato datetime
        df["Inicio"] = pd.to_datetime(df["Inicio"])
        df["Fin"] = pd.to_datetime(df["Fin"])
        return df
    else:
        return None

df = cargar_datos()

if df is None:
    st.error("⚠️ No se encontró el archivo 'cronograma.csv' en el directorio. Por favor, asegúrate de crearlo junto a este script.")
    st.stop()

# ==========================================
# MENÚ DE NAVEGACIÓN LATERAL
# ==========================================
st.sidebar.title("CASIS Guatemala")
paginas = ["Gantt"] + df["Fase"].unique().tolist() + ["Imágenes del Proyecto"]

# Usamos botones de sidebar para cambiar de página de forma fluida
for p in paginas:
    if st.sidebar.button(p, use_container_width=True):
        cambiar_pagina(p)
        st.rerun()

# ==========================================
# RENDERIZADO DE PÁGINAS
# ==========================================

# FUNCIÓN: Renderizador de PDFs incrustado
def mostrar_pdf(archivo_pdf):
    # Reemplaza esta URL con la ruta RAW de tu propio repositorio
    # Formato: https://raw.githubusercontent.com/<USUARIO>/<REPOSITORIO>/<RAMA>/<CARPETA>/
    github_raw_base_url = "https://raw.githubusercontent.com/ujoshlord/casis/main/"
    url_completa = github_raw_base_url + archivo_pdf
    
    try:
        response = requests.get(url_completa)
        if response.status_code == 200:
            base64_pdf = base64.b64encode(response.content).decode('utf-8')
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)
        else:
            st.warning(f"📄 No se pudo descargar '{archivo_pdf}'. Código de estado: {response.status_code}. Verifica que el archivo exista en el repositorio.")
    except Exception as e:
        st.error(f"⚠️ Ocurrió un error al intentar conectar con GitHub: {e}")

# PÁGINA 1: DIAGRAMA DE GANTT
if st.session_state.pagina_actual == "Gantt":
    st.title("Cronograma SCG-Transmetro")
    
    # Renderizar Gantt
    fig = px.timeline(
        df, x_start="Inicio", x_end="Fin", y="Tarea", color="Fase",
        hover_data={"Inicio": "|%d %b %Y", "Fin": "|%d %b %Y", "PDF": True},
        title="Diagrama de Gantt"
    )
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(height=600, xaxis_title="Timeline", yaxis_title="")
    
    st.plotly_chart(fig, use_container_width=True)

# PÁGINAS DINÁMICAS POR FASE (Lector de PDF)
elif st.session_state.pagina_actual in df["Fase"].unique():
    fase_seleccionada = st.session_state.pagina_actual
    archivo_pdf_correspondiente = df[df["Fase"] == fase_seleccionada]["PDF"].iloc[0]
    
    st.title(f"📖 Detalles de la {fase_seleccionada}")
    
    # Mención especial solicitada para Fase 2
    if fase_seleccionada == "Fase 2: Requerimientos":
        st.info("El entregable clave de esta fase es el **Analisis de sistemas: Transmetro**.")
    
    st.markdown(f"**Archivo correspondiente:** `{archivo_pdf_correspondiente}`")
    
    # Mostrar el PDF
    mostrar_pdf(archivo_pdf_correspondiente)
    
    if st.button("⬅️ Volver al Gantt"):
        cambiar_pagina("Gantt")
        st.rerun()

# PÁGINA: IMÁGENES DEL PROYECTO
elif st.session_state.pagina_actual == "Imágenes del Proyecto":
    st.title("🖼️ Galería de Imágenes del Proyecto")
    st.write("En esta sección puedes colocar pantallazos de la App Web (Demo), Diagramas Entidad-Relación y diagramas UML.")
    
    cols = st.columns(2)
    with cols[0]:
        st.caption("Bus")
        st.image("https://www.guatemala.com/fotos/201607/Transmetro-885x500.jpg")
    with cols[1]:
        st.caption("Otro bus jeje")
        st.image("https://tse4.mm.bing.net/th/id/OIP.FGQkd92-764XcRrxWmff3gHaHa?r=0&rs=1&pid=ImgDetMain&o=7&rm=3")
        
    if st.button("⬅️ Volver al Gantt"):
        cambiar_pagina("Gantt")
        st.rerun()