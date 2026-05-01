import streamlit as st
from PIL import Image
import io
import gc
from rembg import remove

# Configurazione pagina
st.set_page_config(
    page_title="Rimuovi Sfondo",
    page_icon="🖼️",
    layout="centered"
)

# Titolo
st.title("🖼️ Rimuovi Sfondo Immagini")
st.markdown("Carica una foto e rimuovi lo sfondo automaticamente")

# Separatore
st.divider()

# Area di upload
uploaded_file = st.file_uploader(
    "📸 Scegli un'immagine...",
    type=["jpg", "jpeg", "png", "webp"],
    help="Formati supportati: JPG, PNG, WEBP"
)

if uploaded_file is not None:
    # === ELABORAZIONE IMMAGINE ===
    try:
        # Leggi l'immagine
        image_bytes = uploaded_file.read()
        input_image = Image.open(io.BytesIO(image_bytes))
        
        # Mostra anteprima originale
        col1, col2 = st.columns(2)
        with col1:
            st.image(input_image, caption="📷 Immagine Originale", use_container_width=True)
        
        # Rimuovi sfondo con indicatore di caricamento
        with st.spinner("✨ Rimozione sfondo in corso..."):
            output_image = remove(input_image)
        
        # Mostra risultato
        with col2:
            st.image(output_image, caption="✨ Senza Sfondo", use_container_width=True)
        
        # Prepara il file per il download
        buf = io.BytesIO()
        output_image.save(buf, format="PNG")
        byte_im = buf.getvalue()
        
        # Bottone download
        st.download_button(
            label="💾 Scarica PNG",
            data=byte_im,
            file_name="senza_sfondo.png",
            mime="image/png"
        )
        
        # === 🔥 PULIZIA IMMEDIATA DELLA MEMORIA ===
        # Elimina i riferimenti alle immagini per liberare RAM
        del input_image
        del output_image
        del image_bytes
        del byte_im
        buf.close()
        
        # Forza garbage collection
        gc.collect()
        
        # Mostra messaggio di conferma privacy
        st.success("🟢 Elaborazione completata. L'immagine non è stata salvata sul server.")
        
    except Exception as e:
        st.error(f"❌ Errore durante l'elaborazione: {str(e)}")
else:
    # Messaggio quando nessuna foto è caricata
    st.info("👆 Clicca sopra per caricare un'immagine")

# Footer informativo
st.divider()
st.caption("🔒 Le immagini vengono eliminate immediatamente dopo il download. Nessun dato viene salvato.")
