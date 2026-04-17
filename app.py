import streamlit as st
import pandas as pd
import requests
import base64
from datetime import datetime
from streamlit_js_eval import get_geolocation

st.set_page_config(page_title="SOFAMEX Pro", page_icon="🏢")

# CONFIGURACIÓN
URL_BUZON_DRIVE = "https://script.google.com/macros/s/AKfycbwZN6RA1YztbOQ9MkZzHPno2ASfBbmGaneUFgwbp9a67fpPaiqH4KMVbwdhSR8APYA1/exec"
SHEET_ID = "1u304ePiJ50UsSBLEANdVZipPfgSQ0ukQCUSnGhZkqY0"
URL_LECTURA = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Sucursales"

st.title("🏢 Sistema de Asistencia SOFAMEX")

location = get_geolocation()

with st.container():
    pin = st.text_input("PIN de Colaborador", type="password")
    tipo = st.radio("Movimiento", ["Entrada", "Salida"], horizontal=True)
    foto = st.camera_input("Captura de Rostro")

    if st.button("REGISTRAR AHORA"):
        if pin and foto and location:
            try:
                # 1. Validar PIN
                df = pd.read_csv(URL_LECTURA)
                df.columns = df.columns.str.strip()
                user = df[df['PIN'].astype(str) == str(pin).strip()]

                if not user.empty:
                    nombre_user = user.iloc[0]['Nombre']
                    st.info(f"Cargando registro para {nombre_user}...")

                    # 2. Convertir foto a formato que entiende el buzón
                    foto_bytes = foto.getvalue()
                    foto_b64 = base64.b64encode(foto_bytes).decode()

                    # 3. Enviar foto al buzón de Drive
                    res_foto = requests.post(URL_BUZON_DRIVE, 
                                           json={"foto": foto_b64, "nombre": nombre_user})
                    url_foto_drive = res_foto.text

                    # 4. Guardar todo en el Sheet de Registros
                    # Usamos el método que ya tenías de st.connection
                    from streamlit_gsheets import GSheetsConnection
                    conn = st.connection("gsheets", type=GSheetsConnection)
                    
                    nuevo = pd.DataFrame([{
                        "Fecha": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                        "Nombre": nombre_user,
                        "Sucursal": "App PC",
                        "Área": user.iloc[0]['Área'],
                        "Movimiento": tipo,
                        "Latitud": location['coords']['latitude'],
                        "Longitud": location['coords']['longitude'],
                        "Foto (Enlace)": url_foto_drive
                    }])

                    df_r = conn.read(worksheet="Registros", ttl=0)
                    df_final = pd.concat([df_r, nuevo], ignore_index=True)
                    conn.update(worksheet="Registros", data=df_final)

                    st.success("✅ ¡Registro y Foto guardados correctamente!")
                    st.balloons()
                else:
                    st.error("PIN incorrecto")
            except Exception as e:
                st.error(f"Error: {e}")
