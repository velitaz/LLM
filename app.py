import os
import streamlit as st
import base64
from openai import OpenAI

# Configuración de la página
st.set_page_config(page_title="Análisis de Imagen con IA", layout="centered", initial_sidebar_state="collapsed")

# --- Estilos personalizados ---
st.markdown("""
    <style>
    .main {
        background-color: #f7f7f7;
    }
    .stButton > button {
        background-color: #ff4b4b;
        color: white;
        border-radius: 8px;
        height: 48px;
        font-size: 16px;
    }
    .stTextInput, .stTextArea {
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- Título principal con emojis ---
st.markdown("<h1 style='text-align: center;'>🧠✨ Análisis Inteligente de Imágenes</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 18px;'>Carga una imagen y obtén una descripción detallada con ayuda de inteligencia artificial.</p>", unsafe_allow_html=True)
st.divider()

# --- Entrada de API Key ---
with st.expander("🔐 Ingresar API Key de OpenAI", expanded=True):
    ke = st.text_input("Ingresa tu clave privada aquí", type="password")
    os.environ['OPENAI_API_KEY'] = ke

api_key = os.environ.get('OPENAI_API_KEY', '')

client = OpenAI(api_key=api_key)

# --- Carga de imagen ---
uploaded_file = st.file_uploader("📷 Sube una imagen (JPG, PNG, JPEG)", type=["jpg", "jpeg", "png"])

if uploaded_file:
    st.image(uploaded_file, caption=f"Imagen cargada: {uploaded_file.name}", use_container_width=True)

# --- Detalles adicionales opcionales ---
show_details = st.toggle("¿Quieres agregar contexto adicional?", value=False)

if show_details:
    additional_details = st.text_area("📝 Escribe el contexto de la imagen aquí")

# --- Botón para analizar imagen ---
analyze_button = st.button("🔍 Analizar imagen")

# --- Lógica de análisis con OpenAI ---
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode("utf-8")

if uploaded_file and api_key and analyze_button:
    with st.spinner("Analizando la imagen con IA..."):
        base64_image = encode_image(uploaded_file)

        prompt_text = "Describe en español lo que ves en esta imagen."

        if show_details and additional_details:
            prompt_text += f"\n\nContexto adicional proporcionado por el usuario:\n{additional_details}"

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
                ],
            }
        ]

        try:
            full_response = ""
            message_placeholder = st.empty()
            for completion in client.chat.completions.create(
                model="gpt-4o", messages=messages, max_tokens=1200, stream=True
            ):
                if completion.choices[0].delta.content is not None:
                    full_response += completion.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        except Exception as e:
            st.error(f"❌ Ocurrió un error: {e}")

# --- Mensajes de advertencia si algo falta ---
elif analyze_button:
    if not uploaded_file:
        st.warning("⚠️ Por favor sube una imagen antes de analizar.")
    if not api_key:
        st.warning("⚠️ Necesitas ingresar tu API Key para continuar.")
