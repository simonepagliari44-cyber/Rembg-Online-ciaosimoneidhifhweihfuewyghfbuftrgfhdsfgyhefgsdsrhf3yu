import streamlit as st
from PIL import Image
import io
import requests
from rembg import remove

st.set_page_config(page_title="Rimuovi Sfondo", page_icon="🖼️")
st.title("🖼️ Rimuovi Sfondo Immagini")

# ============================================================
# CONFIGURAZIONE PROXY PRIVATO
# ============================================================
PROXY_URL = "https://cors-proxy.simonepagliari44.workers.dev"
SECRET_KEY = "mia-app-famiglia-2024"  # Deve essere uguale a quella nel worker

def call_proxy(image_bytes, target_api):
    """Chiama il proxy con autenticazione"""
    proxy_full_url = f"{PROXY_URL}?url={target_api}"
    
    headers = {
        "X-API-Key": SECRET_KEY  # 🔐 Chiave di accesso
    }
    
    files = {
        "image_file": ("image.png", image_bytes, "image/png")
    }
    
    response = requests.post(proxy_full_url, headers=headers, files=files)
    return response

# ============================================================
# INTERFACCIA STREAMLIT
# ============================================================
uploaded_file = st.file_uploader("Scegli un'immagine...", type=["jpg", "png", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    col1, col2 = st.columns(2)
    col1.image(image, caption="Originale")
    
    with st.spinner("✨ Sto rimuovendo lo sfondo..."):
        # Usa rembg direttamente (locale) - più veloce
        output = remove(image)
    
    col2.image(output, caption="Senza sfondo")
    
    buf = io.BytesIO()
    output.save(buf, format="PNG")
    st.download_button("💾 Scarica PNG", buf.getvalue(), "risultato.png")
