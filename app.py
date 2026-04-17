import streamlit as st
import pandas as pd
import requests
import base64
from datetime import datetime
from streamlit_js_eval import get_geolocation

st.set_page_config(page_title="SOFAMEX Pro", page_icon="🏢")

# --- CONFIGURACIÓN ---
URL_APPS_SCRIPT = "https://script.google.com/macros/s/AKfycbzJWfLCyGR91LCJmQI1eHFC2BBiHXUDcwDEmGlVSVIp6SEUn-76e2S7KwsIVLZBvTa4Vw/exec"
SHEET_ID = "1hjnZ9H6Q-6-oOsblegb7GJY3nCuXtHmr0R5e5bCAucw"
URL_LECTURA = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Sucursales"

def obtener_ip():
    try:
        return requests.get('https://api.ipify.org').text
    except:
        return "IP Desconocida"

st.title("🏢 Registro de Asistencia SOFAMEX")

location = get_geolocation()

with st.container():
    pin = st.text_input("PIN de Colaborador", type="password")
    tipo = st.radio("Movimiento", ["Entrada", "Salida"], horizontal=True)
    foto = st.camera_input("Captura de Rostro")

    if st.button("REGISTRAR AHORA"):
        if pin and foto and location:
            try:
                df = pd.read_csv(URL_LECTURA)
                df.columns = df.columns.str.strip()
                user = df[df['PIN'].astype(str) == str(pin).strip()]

                if not user.empty:
                    nombre_user = user.iloc[0]['Nombre']
                    area_user = user.iloc[0]['Área']
                    ip_actual = obtener_ip()
                    
                    st.info(f"Validando credenciales para {nombre_user}...")

                    foto_b64 = base64.b64encode(foto.getvalue()).decode()

                    datos_a_enviar = {
                        "nombre": nombre_user,
                        "area": area_user,
                        "movimiento": tipo,
                        "lat": location['coords']['latitude'],
                        "lng": location['coords']['longitude'],
                        "foto": foto_b64,
                        "ip": ip_actual
                    }

                    respuesta = requests.post(URL_APPS_SCRIPT, json=datos_a_enviar)

                    if respuesta.text == "Éxito":
                        st.success(f"✅ ¡Registro guardado! Hola {nombre_user}.")
                        st.balloons()
                    elif "Error:" in respuesta.text:
                        st.error(f"🛑 {respuesta.text}")
                    else:
                        st.warning(f"Respuesta del servidor: {respuesta.text}")
                else:
                    st.error("❌ PIN incorrecto")
            except Exception as e:
                st.error(f"Error de conexión: {e}")
        else:
            st.warning("⚠️ Falta PIN, Foto o permiso de GPS.")
