import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_js_eval import get_geolocation

# Configuración de página
st.set_page_config(page_title="Asistencia SOFAMEX", page_icon="🏢")

st.title("🏢 Registro de Asistencia SOFAMEX")
st.write("Validación con Cámara y GPS")

# --- CONEXIÓN DIRECTA (Solución al HTTPError) ---
# Extraemos el ID del sheet de tus Secrets
try:
    full_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    sheet_id = full_url.split("/d/")[1].split("/")[0]
except:
    st.error("❌ Error: No se encontró el link del Sheet en los Secrets.")
    st.stop()

# URLs de exportación directa para evitar bloqueos de permisos
url_usuarios = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Sucursales"
url_registros = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Registros"

# --- CAPTURA DE GPS ---
location = get_geolocation()

# --- INTERFAZ DE USUARIO ---
with st.container():
    pin_input = st.text_input("Ingresa tu PIN", type="password")
    tipo_registro = st.selectbox("Movimiento", ["Entrada", "Salida"])
    
    # Cámara nativa de Streamlit (No falla en PC/Móvil)
    foto_capturada = st.camera_input("Toma tu foto para el registro")

    if st.button("CONFIRMAR ASISTENCIA"):
        if not pin_input or foto_capturada is None:
            st.warning("⚠️ Debes ingresar tu PIN y capturar tu fotografía.")
        elif location is None:
            st.error("⚠️ Es obligatorio activar el GPS y dar permiso para registrarte.")
        else:
            try:
                # 1. Leer usuarios usando la URL de exportación directa
                df_usuarios = pd.read_csv(url_usuarios)
                
                # Limpiar nombres de columnas por si hay espacios
                df_usuarios.columns = df_usuarios.columns.str.strip()
                
                # Validar PIN
                usuario = df_usuarios[df_usuarios['PIN'].astype(str) == str(pin_input)]
                
                if not usuario.empty:
                    nombre = usuario.iloc[0]['Nombre']
                    area = usuario.iloc[0]['Área']
                    
                    lat = location['coords']['latitude']
                    lon = location['coords']['longitude']
                    
                    # 2. Preparar el registro
                    # NOTA: La escritura directa requiere una lógica más avanzada o usar la librería gsheets. 
                    # Por ahora, validaremos que la lectura funcione.
                    st.success(f"✅ ¡PIN Validado! Hola {nombre}.")
                    st.info(f"📍 Ubicación capturada: {lat}, {lon}")
                    
                    # Para escribir, usaremos el método de st-gsheets-connection que ya configuraste
                    from streamlit_gsheets import GSheetsConnection
                    conn = st.connection("gsheets", type=GSheetsConnection)
                    
                    nuevo_dato = pd.DataFrame([{
                        "Fecha": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                        "Nombre": nombre,
                        "Sucursal": "Web App",
                        "Área": area,
                        "Movimiento": tipo_registro,
                        "Latitud": lat,
                        "Longitud": lon,
                        "Dispositivo": "Streamlit Cloud",
                        "Foto (Enlace)": "Imagen capturada"
                    }])
                    
                    df_actual = conn.read(worksheet="Registros", ttl=0)
                    df_final = pd.concat([df_actual, nuevo_dato], ignore_index=True)
                    conn.update(worksheet="Registros", data=df_final)
                    
                    st.success("✨ Registro guardado en el Excel correctamente.")
                    st.balloons()
                else:
                    st.error("❌ PIN no reconocido en la base de datos.")
            except Exception as e:
                st.error(f"❌ Error de conexión: {e}")
                st.info("Asegúrate de que el Sheet esté en 'Cualquier persona con el enlace puede leer'.")
