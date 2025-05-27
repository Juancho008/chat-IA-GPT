FROM python:3.12.1

WORKDIR /app

# Instala dependencias del sistema necesarias (incluye git)
RUN apt-get update && apt-get install -y git && apt-get clean

# Copia el archivo de requisitos
COPY requirements.txt .

# Instala dependencias en orden correcto
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir sentence-transformers langchain-community

# Instala dependencias restantes de tu app
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto de la app
COPY documentos documentos
COPY . .

# Script de inicio
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Expone puertos
EXPOSE 8501
EXPOSE 8010

CMD ["/start.sh"]
