import os
import streamlit as st
import chromadb
import tempfile
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from sentence_transformers import SentenceTransformer

# Configuración de ChromaDB fuera del try-except
try:
    chroma_client = chromadb.HttpClient(host="192.168.30.15", port=8010)  # Corrección en la URL
    print("Conexión exitosa a ChromaDB")
except Exception as e:
    st.error(f"Error al conectar con ChromaDB: {str(e)}")
    chroma_client = None  # Evita que otros errores se propaguen

# Nombre del archivo y del índice
FILE_LIST = "archivos.txt"
INDEX_NAME = "taller"

def load_name_files(path):
    """Carga la lista de archivos desde el archivo FILE_LIST."""
    if not os.path.exists(path):
        return []
    with open(path, "r") as file:
        return [line.strip() for line in file]

def save_name_files(path, new_files):
    """Guarda los nombres de nuevos archivos en FILE_LIST evitando duplicados."""
    old_files = load_name_files(path)
    with open(path, "a") as file:
        for item in new_files:
            if item not in old_files:
                file.write(item + "\n")
                old_files.append(item)
    return old_files

def clean_files(path):
    """Limpia el archivo FILE_LIST y la colección en ChromaDB."""
    with open(path, "w") as file:
        pass  # Borra el contenido del archivo
    if chroma_client:
        chroma_client.delete_collection(name=INDEX_NAME)
        chroma_client.create_collection(name=INDEX_NAME)
    return True

def check_collection_exists():
    """Verifica si la colección existe en ChromaDB."""
    if chroma_client:
        collections = chroma_client.list_collections()  # Corrección en el método
        return INDEX_NAME in [col.name for col in collections]
    return False

def text_to_chromadb(pdf):
    """Convierte el texto de un PDF y lo almacena en ChromaDB."""
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_filepath = os.path.join(temp_dir, pdf.name)
            with open(temp_filepath, "wb") as f:
                f.write(pdf.getvalue())

            loader = PyPDFLoader(temp_filepath)
            text = loader.load()

            with st.spinner(f"Creando embedding para: {pdf.name}"):
                create_embeddings(pdf.name, text)
            return True
    except Exception as e:
        st.error(f"Error al procesar el archivo {pdf.name}: {str(e)}")
        return False

def create_embeddings(file_name, text):
    """Crea embeddings y los almacena en ChromaDB."""
    try:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=160,
            length_function=len,
            separators=["\n\n", ".", "?", "!"],
            keep_separator=True,
        )
        chunks = text_splitter.split_documents(text)

        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-mpnet-base-v2",
            model_kwargs={"device": "cpu"},  # Usa CPU para evitar problemas con PyTorch
        )

        if chroma_client:
            Chroma.from_documents(
                chunks, embeddings, client=chroma_client, collection_name=INDEX_NAME
            )
        return True
    except Exception as e:
        st.error(f"Error al crear embeddings para {file_name}: {str(e)}")
        return False

# Configuración de ChromaDB fuera del try-except
try:
    collections = chroma_client.list_collections()  # Corrección en el método
    print("Conexión exitosa. Colecciones disponibles:", collections)
except Exception as e:
    print(f"Error al conectar con ChromaDB: {e}")

# Mostrar los archivos cargados desde archivos.txt
uploaded_files = load_name_files(FILE_LIST)
if uploaded_files:
    st.write(f"Archivos cargados: {', '.join(uploaded_files)}")
else:
    st.write("No hay archivos cargados.")
