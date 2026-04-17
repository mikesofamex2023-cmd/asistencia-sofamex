import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_js_eval import get_geolocation

st.set_page_config(page_title="SOFAMEX Asistencia", page_icon="🏢")

# 1. Obtener el ID del Sheet desde tus Secrets
try:
    sheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    sheet_id = sheet_url.split("/d/")[1].split("/")[0]
except:
    st.error("Configura el link del Sheet en los Secrets.")
    st.stop()

# URLs de lectura directa (Esto evita el Error 400)
url_sucursales = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Sucursales"

st.title("🏢 Registro SOFAMEX")

location = get_geolocation()

with st.container():
    pin_input = st.text_input("Ingresa tu PIN", type="password")
    tipo = st.radio("Movimiento", ["Entrada", "Salida"], horizontal=True)
    foto = st.camera_input("Captura de rostro")

    if st.button("CONFIRMAR REGISTRO"):
        if pin_input and foto and location:
            try:
                # Leer datos de sucursales directamente
                df_u = pd.read_csv(url_sucursales)
                df_u.columns = df_u.columns.str.strip() # Limpiar espacios
                
                # Validar PIN
                user = df_u[df_u['PIN'].astype(str) == str(pin_input).strip()]
                
                if not user.empty:
                    nombre = user.iloc[0]['Nombre']
                    st.success(f"✅ ¡PIN Correcto! Hola {nombre}")
                    
                    # Para GUARDAR (update), sí usaremos la conexión oficial
                    from streamlit_gsheets import GSheetsConnection
                    conn = st.connection("gsheets", type=GSheetsConnection)
                    
                    nuevo = pd.DataFrame([{
                        "Fecha": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                        "Nombre": nombre,
                        "Sucursal": "App Python",
                        "Área": user.iloc[0]['Área'],
                        "Movimiento": tipo,
                        "Latitud": location['coords']['latitude'],
                        "Longitud": location['coords']['longitude'],
                        "Foto (Enlace)": "Imagen Capturada"
                    }])
                    
                    # Leer y Actualizar
                    df_r = conn.read(worksheet="Registros", ttl=0)
                    df_final = pd.concat([df_r, nuevo], ignore_index=True)
                    conn.update(worksheet="Registros", data=df_final)
                    
                    st.success("✨ Registro guardado en el Sheet.")
                    st.balloons()
                else:
                    st.error("❌ PIN no encontrado.")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("⚠️ Captura PIN, Foto y permite el GPS.")
