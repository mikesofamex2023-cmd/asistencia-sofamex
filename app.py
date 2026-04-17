import streamlit as st
import pandas as pd
import requests
import base64
from datetime import datetime
from streamlit_js_eval import get_geolocation

st.set_page_config(page_title="SOFAMEX Pro", page_icon="🏢")

# CONFIGURACIÓN - PEGA TU URL AQUÍ
URL_APPS_SCRIPT = "https://script.google.com/macros/s/AKfycbwZN6RA1YztbOQ9MkZzHPno2ASfBbmGaneUFgwbp9a67fpPaiqH4KMVbwdhSR8APYA1/exec"
SHEET_ID = "1u304ePiJ50UsSBLEANdVZipPfgSQ0ukQCUSnGhZkqY0"
URL_LECTURA = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Sucursales"

st.title("🏢 Registro de Asistencia SOFAMEX")

location = get_geolocation()

with st.container():
    pin = st.text_input("PIN de Colaborador", type="password")
    tipo = st.radio("Movimiento", ["Entrada", "Salida"], horizontal=True)
    foto = st.camera_input("Captura de Rostro")

    if st.button("REGISTRAR AHORA"):
        if pin and foto and location:
            try:
                # 1. Leer usuarios (Esto sí funciona sin error 400)
                df = pd.read_csv(URL_LECTURA)
                df.columns = df.columns.str.strip()
                user = df[df['PIN'].astype(str) == str(pin).strip()]

                if not user.empty:
                    nombre_user = user.iloc[0]['Nombre']
                    area_user = user.iloc[0]['Área']
                    st.info(f"Enviando registro de {nombre_user}...")

                    # 2. Preparar foto
                    foto_b64 = base64.b64encode(foto.getvalue()).decode()

                    # 3. Enviar TODO al Apps Script
                    datos_a_enviar = {
                        "nombre": nombre_user,
                        "area": area_user,
                        "movimiento": tipo,
                        "lat": location['coords']['latitude'],
                        "lng": location['coords']['longitude'],
                        "foto": foto_b64
                    }

                    respuesta = requests.post(URL_APPS_SCRIPT, json=datos_a_enviar)

                    if "Éxito" in respuesta.text:
                        st.success(f"✅ ¡Registro y Foto guardados! Hola {nombre_user}.")
                        st.balloons()
                    else:
                        st.error(f"Error en el servidor: {respuesta.text}")
                else:
                    st.error("❌ PIN incorrecto")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("⚠️ Falta PIN, Foto o permiso de GPS.")
