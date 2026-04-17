import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_js_eval import get_geolocation
from streamlit_gsheets import GSheetsConnection

# Configuración de página
st.set_page_config(page_title="Asistencia SOFAMEX", page_icon="🏢")

st.title("🏢 Registro de Asistencia SOFAMEX")
st.write("Validación con Cámara y GPS")

# --- CONEXIÓN ---
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    full_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    sheet_id = full_url.split("/d/")[1].split("/")[0]
except:
    st.error("❌ Error: No se encontró el link del Sheet en los Secrets.")
    st.stop()

# --- CAPTURA DE GPS ---
location = get_geolocation()

# --- INTERFAZ ---
with st.container():
    pin_input = st.text_input("Ingresa tu PIN", type="password")
    tipo_registro = st.selectbox("Movimiento", ["Entrada", "Salida"])
    foto_capturada = st.camera_input("Toma tu foto para el registro")

    if st.button("CONFIRMAR ASISTENCIA"):
        if not pin_input or foto_capturada is None:
            st.warning("⚠️ Debes ingresar tu PIN y capturar tu fotografía.")
        elif location is None:
            st.error("⚠️ Es obligatorio activar el GPS.")
        else:
            try:
                # 1. Leer usuarios (ttl=0 para que siempre esté actualizado)
                df_usuarios = conn.read(worksheet="Sucursales", ttl=0)
                
                # LIMPIEZA TOTAL DE COLUMNAS (Para evitar el error 'Nombre')
                df_usuarios.columns = df_usuarios.columns.str.strip().str.capitalize()
                
                # Buscar el PIN (Limpiamos también los datos por si acaso)
                # Buscamos en la columna 'Pin' (capitalizada arriba)
                df_usuarios['Pin'] = df_usuarios['Pin'].astype(str).str.strip()
                usuario = df_usuarios[df_usuarios['Pin'] == str(pin_input).strip()]
                
                if not usuario.empty:
                    # Usamos los nombres capitalizados
                    nombre = usuario.iloc[0]['Nombre']
                    area = usuario.iloc[0]['Área']
                    
                    lat = location['coords']['latitude']
                    lon = location['coords']['longitude']
                    
                    # 2. Registrar en la pestaña 'Registros'
                    nuevo_dato = pd.DataFrame([{
                        "Fecha": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                        "Nombre": nombre,
                        "Sucursal": "Sucursal Web",
                        "Área": area,
                        "Movimiento": tipo_registro,
                        "Latitud": lat,
                        "Longitud": lon,
                        "Dispositivo": "Streamlit",
                        "Foto (Enlace)": "Capturada"
                    }])
                    
                    df_actual = conn.read(worksheet="Registros", ttl=0)
                    df_final = pd.concat([df_actual, nuevo_dato], ignore_index=True)
                    conn.update(worksheet="Registros", data=df_final)
                    
                    st.success(f"✅ ¡Registro exitoso! Hola {nombre}.")
                    st.balloons()
                else:
                    st.error(f"❌ PIN {pin_input} no encontrado. Columnas detectadas: {list(df_usuarios.columns)}")
            
            except Exception as e:
                st.error(f"❌ Error: {e}")
