import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
from streamlit_js_eval import get_geolocation # Para la ubicación real

# Configuración visual de SOFAMEX
st.set_page_config(page_title="Asistencia SOFAMEX", page_icon="🏢")

st.title("🏢 Registro de Asistencia SOFAMEX")
st.write("Sistema de validación con Cámara y GPS")

# Conexión al Google Sheet (ID: 1u304ePiJ50UsSBLEANdVZipPfgSQ0ukQCUSnGhZkqY0)
conn = st.connection("gsheets", type=GSheetsConnection)

# --- CAPTURA DE GEOLOCALIZACIÓN ---
# Esto solicita permiso al navegador para obtener el GPS
location = get_geolocation()

# --- FORMULARIO DE REGISTRO ---
with st.container():
    pin_input = st.text_input("Ingresa tu PIN", type="password")
    tipo_registro = st.selectbox("Movimiento", ["Entrada", "Salida"])
    
    # Cámara estable de Streamlit
    foto_capturada = st.camera_input("Toma tu foto para el registro")

    if st.button("CONFIRMAR ASISTENCIA"):
        if not pin_input or foto_capturada is None:
            st.warning("⚠️ Debes ingresar tu PIN y capturar tu fotografía.")
        elif location is None:
            st.error("⚠️ Es obligatorio activar el GPS y dar permiso de ubicación para registrarte.")
        else:
            # 1. Leer pestaña Sucursales para validar PIN
            df_usuarios = conn.read(worksheet="Sucursales", ttl=0)
            
            # Buscar usuario
            usuario = df_usuarios[df_usuarios['PIN'].astype(str) == str(pin_input)]
            
            if not usuario.empty:
                nombre = usuario.iloc[0]['Nombre']
                area = usuario.iloc[0]['Área']
                
                # Extraer Lat/Lng del componente de geolocalización
                lat = location['coords']['latitude']
                lon = location['coords']['longitude']
                
                # 2. Preparar el nuevo registro según tu estructura de Sheet
                nuevo_dato = pd.DataFrame([{
                    "Fecha": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    "Nombre": nombre,
                    "Sucursal": "Detectada vía Web",
                    "Área": area,
                    "Movimiento": tipo_registro,
                    "Latitud": lat,
                    "Longitud": lon,
                    "Dispositivo": "Navegador Web",
                    "Foto (Enlace)": "Imagen en proceso..." 
                }])
                
                # 3. Leer registros actuales y concatenar el nuevo
                df_registros = conn.read(worksheet="Registros", ttl=0)
                df_final = pd.concat([df_registros, nuevo_dato], ignore_index=True)
                
                # 4. Actualizar el Sheet en la nube
                conn.update(worksheet="Registros", data=df_final)
                
                st.success(f"✅ ¡Registro guardado! Hola {nombre}. (Ubicación: {lat}, {lon})")
                st.balloons()
            else:
                st.error("❌ PIN no reconocido.")
