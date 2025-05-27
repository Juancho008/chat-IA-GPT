from utils import *
import streamlit as st
import os
import shutil
import tempfile
import base64
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_community.chat_models import ChatOpenAI
from langchain.chains.question_answering import load_qa_chain
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-mpnet-base-v2")

try:
    # clave de la api de gpt
    OPENAI_API_KEY = os.getenv('API_KEY')
    # Configurar en base a tu nombre de carpetas y si se sube al servidor subirlo con la direccion ip seguido de los volumenes 192.168.30.38\\var\\wwww\
    CARPETA_DESTINO = "documentos"

    # Definir la estructura de las páginas
    def pagina_principal():
        st.header("Chatbot Parlamentario")
        st.markdown("Por favor realizá tus preguntas lo más específico posible")

        user_question = st.text_input("Pregunta:")
        if user_question:
            # Creación de embeddings utilizando HuggingFaceEmbeddings
            embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-mpnet-base-v2",
                model_kwargs={
                    "device": "cpu"
                },  # Usa CPU para evitar problemas con PyTorch
            )

            # Realiza una búsqueda semántica en ChromaDB y obtiene documentos similares
            vstore = Chroma(
                client=chroma_client,
                collection_name=INDEX_NAME,
                embedding_function=embeddings,
            )

            # Búsqueda de documentos similares basada en la pregunta del usuario
            docs = vstore.similarity_search(user_question, 20)

            # Carga un modelo de Chat de OpenAI y realiza la cadena de procesamiento de preguntas y respuestas
            llm = ChatOpenAI(model_name="gpt-4", openai_api_key=OPENAI_API_KEY)
            chain = load_qa_chain(llm, chain_type="stuff")
            # viejo
            # respuesta = chain.run(input_documents=docs, question="Actúa como un experto en análisis de información con años de experiencia en la revisión y compresión de textos extensos. Toma el contenido proporcionado y redacta un resumen conciso y claro que capture la esencia del texto original sin perder información crucial.El objetivo es producir un resumen que permita al lector comprender rápidamente el propósito y los argumentos principales sobre el tema." + user_question )
            # nueva actualizacion
            respuesta = chain.run(
                input_documents=docs,
                question="Actúa como un experto en análisis de información y busca informacion sobre"
                + user_question
                + "redacta un resumen conciso y claro que capture la esencia del texto original sin perder información crucial",
            )
            # Mostrar la respuesta junto con el nombre del archivo de donde proviene
            st.write("Respuesta:")
            st.write(respuesta)

            # Mostrar luego los archivos relacionados si hay archivos cargados
            st.write("Archivos relacionados:")
            archivos_mostrados = (
                set()
            )  # Almacena los nombres de los archivos ya mostrados
            for doc in docs:
                nombre_archivo = os.path.basename(
                    doc.metadata["source"]
                )  # Obtener solo el nombre del archivo
                if (
                    nombre_archivo not in archivos_mostrados
                ):  # Verificar si el archivo ya ha sido mostrado
                    archivo_path = os.path.join(CARPETA_DESTINO, nombre_archivo)
                    with open(archivo_path, "rb") as f:
                        data = f.read()
                        base64_encoded = base64.b64encode(data).decode()
                        st.markdown(
                            f'<a href="data:application/pdf;base64,{base64_encoded}" download="{nombre_archivo}">{nombre_archivo}</a>',
                            unsafe_allow_html=True,
                        )
                    archivos_mostrados.add(
                        nombre_archivo
                    )  # Agregar el nombre del archivo a los archivos mostrados

    def segunda_pagina():
        st.title("Carga de Archivos - devs-03")
        st.write("Por favor carga los archivos en formato PDF")
        # Carga la lista de archivos desde FILE_LIST
        archivos = load_name_files(FILE_LIST)

        # Lista para almacenar los nombres de los archivos cargados correctamente
        archivos_cargados_correctamente = []

        # Lista para almacenar los nombres de los archivos no procesados
        archivos_no_procesados = []

        # Carga los archivos PDF mediante un widget de carga de archivos
        files_uploaded = st.file_uploader(
            "Carga tu archivo", type="pdf", accept_multiple_files=True
        )

        # Función para guardar el archivo en la carpeta de destino
        def guardar_archivo(archivo, nombre_archivo, carpeta_destino):
            # Verificar si la carpeta de destino existe, si no, crearla
            if not os.path.exists(carpeta_destino):
                os.makedirs(carpeta_destino)

            # Crear la ruta completa para guardar el archivo
            ruta_archivo = os.path.join(carpeta_destino, nombre_archivo)

            # Guardar el archivo en la carpeta de destino
            with open(ruta_archivo, "wb") as f:
                f.write(archivo.getbuffer())

        # Botón para procesar los archivos cargados
        if st.button("Procesar"):
            for pdf in files_uploaded or []:
                try:
                    if pdf is not None and pdf.name not in archivos:
                        archivos.append(pdf.name)
                        guardar_archivo(
                            pdf, pdf.name, CARPETA_DESTINO
                        )  # Llamada a la función guardar_archivo()
                        archivos_cargados_correctamente.append(pdf.name)
                        text_to_chromadb(pdf)
                except Exception as e:
                    archivos_no_procesados.append(pdf.name)
                    st.error(f"Error al procesar el archivo {pdf.name}: {str(e)}")

            # Guardar los nombres de los archivos no procesados en un archivo de registro
            if archivos_no_procesados:
                with open("archivos_no_procesados.log", "w") as log_file:
                    for archivo in archivos_no_procesados:
                        log_file.write(archivo + "\n")

            # Guardar los nombres de los archivos cargados correctamente en un archivo de registro
            if archivos_cargados_correctamente:
                with open("archivos_cargados_correctamente.log", "w") as log_file:
                    for archivo in archivos_cargados_correctamente:
                        log_file.write(archivo + "\n")

            # Guarda los nombres de los archivos actualizados en FILE_LIST
            archivos = save_name_files(FILE_LIST, archivos)

    # Obtener el parámetro de la URL
    params = st.query_params
    show_second_page = "cargar_archivos" in params

    # Mostrar la página seleccionada
    if show_second_page:
        segunda_pagina()
    else:
        pagina_principal()

except Exception as e:
    st.error(f"Error: {str(e)}")
