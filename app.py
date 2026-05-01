import streamlit as st
from PIL import Image
import io
import requests
from rembg import remove

st.set_page_config(page_title="Rimuovi Sfondo", page_icon="🖼️")
st.title("🖼️ Rimuovi Sfondo Immagini")

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
