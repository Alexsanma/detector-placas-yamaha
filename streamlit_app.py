import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"

# ─── Configuración de página ───
st.set_page_config(
    page_title="Detector de Placas",
    page_icon="assets/icon.png",
    layout="wide",
)

st.title("Detector de Placas Vehiculares")
st.caption("Sistema de control de acceso con YOLO + EasyOCR")

# ─── Sidebar: navegación ───
seccion = st.sidebar.radio(
    "Navegación",
    ["Detectar placa", "Registrar vehículo", "Historial de eventos"],
)

st.sidebar.markdown("---")
st.sidebar.caption("**API:** " + API_URL)
st.sidebar.caption("Asegúrate de que el backend esté corriendo:")
st.sidebar.code("uvicorn main:app --reload", language="bash")


# ─── Helpers ───
def api_disponible() -> bool:
    """Verifica si la API está respondiendo."""
    try:
        return requests.get(f"{API_URL}/", timeout=2).status_code == 200
    except requests.RequestException:
        return False


if not api_disponible():
    st.error("La API no está disponible. Levanta el backend con `uvicorn main:app --reload`.")
    st.stop()


# ─── Sección 1: Detectar placa ───
if seccion == "Detectar placa":
    st.header("Detectar placa en una imagen")

    col_izq, col_der = st.columns([1, 1])

    with col_izq:
        imagen_subida = st.file_uploader(
            "Sube una imagen del vehículo",
            type=["jpg", "jpeg", "png"],
        )
        camera_id = st.number_input("ID de cámara (opcional)", min_value=1, value=1, step=1)

        if imagen_subida is not None:
            st.image(imagen_subida, caption="Imagen cargada", width='stretch')

    with col_der:
        if imagen_subida is not None and st.button("Procesar detección", type="primary"):
            with st.spinner("Procesando imagen..."):
                archivos = {"imagen": (imagen_subida.name, imagen_subida.getvalue(), imagen_subida.type)}
                params = {"camera_id": int(camera_id)}

                try:
                    respuesta = requests.post(
                        f"{API_URL}/detectar",
                        files=archivos,
                        params=params,
                        timeout=60,
                    )
                except requests.RequestException as e:
                    st.error(f"Error de conexión: {e}")
                    st.stop()

            if respuesta.status_code == 200:
                data = respuesta.json()
                st.success(f"Placa detectada: **{data['placa']}**")

                col1, col2 = st.columns(2)
                col1.metric("Tipo de evento", data["tipo_evento"].upper())
                col2.metric("Tipo de vehículo", data["tipo_vehiculo"].upper())

                col3, col4 = st.columns(2)
                col3.metric("Confianza detección", f"{data['confianza_deteccion']:.1%}")
                col4.metric("Confianza OCR", f"{data['confianza_ocr']:.1%}")

                with st.expander("Ver respuesta completa"):
                    st.json(data)
            else:
                detalle = respuesta.json().get("detail", "Error desconocido")
                st.error(f"Error: {detalle}")


# ─── Sección 2: Registrar vehículo ───
elif seccion == "Registrar vehículo":
    st.header("Registrar un vehículo")

    with st.form("form_vehiculo"):
        placa = st.text_input("Placa", placeholder="Ej: ABC123", max_chars=10)
        tipo = st.selectbox("Tipo", ["registrado", "visitante"])
        nombre = st.text_input("Nombre del propietario (opcional)", placeholder="Ej: Juan Pérez")
        enviar = st.form_submit_button("Registrar", type="primary")

    if enviar:
        if not placa.strip():
            st.error("La placa es obligatoria.")
            st.stop()

        payload = {"placa": placa.strip().upper(), "tipo": tipo}
        if nombre.strip():
            payload["nombre"] = nombre.strip()

        try:
            respuesta = requests.post(f"{API_URL}/vehiculos", json=payload, timeout=10)
        except requests.RequestException as e:
            st.error(f"Error de conexión: {e}")
            st.stop()

        if respuesta.status_code == 201:
            data = respuesta.json()
            st.success(f"Vehículo registrado correctamente (ID: {data['id']})")
            st.json(data)
        else:
            detalle = respuesta.json().get("detail", "Error desconocido")
            st.error(f"Error: {detalle}")


# ─── Sección 3: Historial de eventos ───
elif seccion == "Historial de eventos":
    st.header("Historial de eventos")

    if st.button("Actualizar"):
        st.rerun()

    try:
        respuesta = requests.get(f"{API_URL}/eventos", timeout=10)
    except requests.RequestException as e:
        st.error(f"Error de conexión: {e}")
        st.stop()

    if respuesta.status_code == 200:
        eventos = respuesta.json()

        if not eventos:
            st.info("No hay eventos registrados todavía.")
        else:
            st.caption(f"Total de eventos: {len(eventos)}")
            st.dataframe(
                eventos,
                hide_index=True,
                column_config={
                    "id": st.column_config.NumberColumn("ID", width="small"),
                    "placa": st.column_config.TextColumn("Placa", width="small"),
                    "tipo_evento": st.column_config.TextColumn("Evento", width="small"),
                    "confianza": st.column_config.NumberColumn("Confianza", format="%.2f"),
                    "fecha_hora": st.column_config.DatetimeColumn("Fecha", format="DD/MM/YYYY HH:mm:ss"),
                    "camera_id": st.column_config.NumberColumn("Cámara", width="small"),
                },
            )
    else:
        st.error("No se pudieron cargar los eventos.")