# -*- coding: utf-8 -*-

import io
import json
import os
import tempfile
import time
import uuid
import zipfile
from pathlib import Path

import streamlit as st
from PIL import Image, ImageSequence
from dotenv import load_dotenv
from loguru import logger
from rembg import remove

# === FUNZIONE ALTERNATIVA PER CONTROLLARE TIPO FILE (senza imghdr) ===
def is_valid_image(file_bytes, allowed_extensions=['png', 'jpg', 'jpeg', 'gif']):
    """Controlla se i byte del file corrispondono a un'immagine valida"""
    try:
        img = Image.open(io.BytesIO(file_bytes))
        img.verify()
        return True
    except Exception:
        return False

def remove_bg(input_data, path):
    result = remove(input_data)
    img = Image.open(io.BytesIO(result)).convert('RGBA')
    if Path(path).suffix != '.png':
        img.LOAD_TRUNCATED_IMAGES = True
    return img

def gif2frames(input_file, skip_every=1):
    im = Image.open(input_file)
    include_frames = range(0, len(list(ImageSequence.Iterator(im))), skip_every)

    frames = []

    for n, frame in enumerate(ImageSequence.Iterator(im)):
        if n not in include_frames:
            continue
        frame.copy()
        bytes_obj = io.BytesIO()
        frame.save(bytes_obj, format='PNG')
        frames.append((n, bytes_obj.getvalue()))
    return frames

def main():
    if st.sidebar.button('CLEAR'):
        st.session_state['key'] = K
        st.rerun()  # experimental_rerun è deprecato
    st.sidebar.markdown('---')

    accept_multiple_files = True
    accepted_type = ['png', 'jpg', 'jpeg', 'gif']

    uploaded_files = st.sidebar.file_uploader(
        f'Scegli uno o più file (max: {MAX_FILES})',
        type=accepted_type,
        accept_multiple_files=accept_multiple_files,
        key=st.session_state['key'])

    if len(uploaded_files) > MAX_FILES and MAX_FILES != -1:
        st.warning(
            f'Numero massimo di file raggiunto! Solo i primi {MAX_FILES} '
            'verranno processati.')
        uploaded_files = uploaded_files[:MAX_FILES]

    uploaded_files = [x for x in uploaded_files if x]

    if uploaded_files:
        logger.info(f'File caricati: {uploaded_files}')

        progress_bar = st.empty()
        down_btn = st.empty()
        cols = st.empty()
        col1, col2 = cols.columns(2)
        imgs_bytes = []
        frames = []

        IS_GIF = False
        if any(Path(x.name).suffix.lower() == '.gif' for x in uploaded_files):
            IS_GIF = True
            if len(uploaded_files) > 1:
                st.error(
                    'Quando processi un GIF puoi caricare un solo file!')
                return

            dur_text = 'Durata (in millisecondi) di ogni frame:'
            duration = st.sidebar.slider(dur_text, 0, 1000, 100, 10)
            frames = gif2frames(uploaded_files[0])

        for uploaded_file in uploaded_files:
            bytes_data = uploaded_file.getvalue()
            
            # VERIFICA SENZA imghdr
            if not is_valid_image(bytes_data):
                st.error(f'`{uploaded_file.name}` non è un\'immagine valida!')
                continue

            if 'btn' not in st.session_state:
                st.session_state.my_button = True
                imgs_bytes.append((uploaded_file, bytes_data))

        col1.image([x[1] for x in imgs_bytes])

        nobg_imgs = []
        if st.sidebar.button('Rimuovi sfondo'):
            pb = progress_bar.progress(0)

            if frames:
                imgs_bytes = frames

            with st.spinner('Elaborazione in corso...'):
                for n, (uploaded_file, bytes_data) in enumerate(imgs_bytes, start=1):
                    if isinstance(uploaded_file, int):
                        p = Path(str(uploaded_file) + '.png')
                    else:
                        p = Path(uploaded_file.name)

                    img = remove_bg(bytes_data, p)
                    with io.BytesIO() as f:
                        img.save(f, format='PNG', quality=100, subsampling=0)
                        data = f.getvalue()
                    nobg_imgs.append((img, p, data))

                    cur_progress = int(100 / len(imgs_bytes))
                    pb.progress(cur_progress * n)
                time.sleep(1)
                progress_bar.empty()

                nobg_images = [x[0] for x in nobg_imgs]

                if IS_GIF:
                    col2.markdown(
                        '🧪 *Usa [ezgif.com](https://ezgif.com/) per creare '
                        'il file GIF e modificare i frame.*')
                col2.image(nobg_images)

            if len(nobg_imgs) > 1:
                with io.BytesIO() as tmp_zip:
                    with zipfile.ZipFile(tmp_zip, 'w') as z:
                        for img, p, data in nobg_imgs:
                            with tempfile.NamedTemporaryFile() as fp:
                                img.save(fp.name, format='PNG')
                                z.write(fp.name,
                                        arcname=p.name,
                                        compress_type=zipfile.ZIP_DEFLATED)
                    zip_data = tmp_zip.getvalue()

                if IS_GIF:
                    frames_literal = '(frame individuali)'
                else:
                    frames_literal = ''

                down_btn.download_button(
                    label=f'Scarica tutti i risultati {frames_literal}',
                    data=zip_data,
                    file_name=f'risultati_{int(time.time())}.zip',
                    mime='application/zip',
                    key='btn')
            else:
                try:
                    out = nobg_imgs[0]
                    down_btn.download_button(
                        label='Scarica risultato',
                        data=out[-1],
                        file_name=f'{out[1].stem}_nobg.png',
                        mime='image/png',
                        key='btn')
                except IndexError:
                    st.error('Nessuna immagine da processare!')
                finally:
                    st.session_state['key'] = K

if __name__ == '__main__':
    st.set_page_config(page_title='Rimuovi Sfondo',
                       page_icon='✂️',
                       initial_sidebar_state='expanded')
    st.markdown(
        '<style> footer {visibility: hidden;}'
        '#MainMenu {visibility: hidden;}</style>',
        unsafe_allow_html=True)
    logger.add('logs.log')

    load_dotenv()

    MAX_FILES = 10
    if os.getenv('MAX_FILES'):
        MAX_FILES = int(os.getenv('MAX_FILES'))

    # Rimossa la parte Gotify che causava errori
    K = str(uuid.uuid4())
    if 'key' not in st.session_state:
        st.session_state['key'] = K

    main()
