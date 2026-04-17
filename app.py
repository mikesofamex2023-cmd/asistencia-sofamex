import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
from streamlit_js_eval import get_geolocation

st.set_page_config(page_title="Asistencia SOFAMEX", page_icon="🏢")

st.title("🏢 Registro SOFAMEX")

# Conexión simple
conn = st.connection("gsheets", type=GSheetsConnection)

# GPS
location = get_geolocation()

with st.container():
    pin_input = st.text_input("PIN", type="password")
    tipo_registro = st.radio("Movimiento", ["Entrada", "Salida"], horizontal=True)
    foto = st.camera_input("Foto")

    if st.button("REGISTRAR"):
        if pin_input and foto and location:
            try:
                # Leer Sucursales
                df_u = conn.read(worksheet="Sucursales")
                # Limpiar nombres de columnas
                df_u.columns = df_u.columns.str.strip()
                
                # Validar PIN
                user = df_u[df_u['PIN'].astype(str) == str(pin_input).strip()]
                
                if not user.empty:
                    nombre = user.iloc[0]['Nombre']
                    area = user.iloc[0]['Área']
                    
                    # Crear registro
                    nuevo = pd.DataFrame([{
                        "Fecha": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                        "Nombre": nombre,
                        "Sucursal": "Web",
                        "Área": area,
                        "Movimiento": tipo_registro,
                        "Latitud": location['coords']['latitude'],
                        "Longitud": location['coords']['longitude'],
                        "Foto (Enlace)": "Capturada"
                    }])
                    
                    # Escribir en Registros
                    df_r = conn.read(worksheet="Registros")
                    df_final = pd.concat([df_r, nuevo], ignore_index=True)
                    conn.update(worksheet="Registros", data=df_final)
                    
                    st.success(f"✅ ¡Hecho! Hola {nombre}")
                    st.balloons()
                else:
                    st.error("❌ PIN incorrecto")
            except Exception as e:
                st.error(f"Error técnico: {e}")
        else:
            st.warning("⚠️ Falta PIN, Foto o GPS")
