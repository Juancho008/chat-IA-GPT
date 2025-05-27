# Chat-IA-Parlamentario

# Levantar contenedor de docker con Python 3.12.1 y ChromaDB
Desde la consola nos posicionamos en la carpeta donde se encuentran los archivos
Lanzamos el comando " docker-compose up --build -d "

# En el navegador
para ver la aplicacion " localhost:8501 " o " direccion-del-servidor:8501 "

## Configuracion antes de levantar en sevidor
dentro de docker-compose.yaml en la seccion volumes de python cambiar por la direccion en la que se encuentra los archivos de la aplicacion

# Volumen montado para persistir datos
volumes:
- ./apps:/home/sistemas/entorno_py/html_py

### Para listar contenedor activos e inactivos " docker ps -a " 
### Para listar imagenes activas e inactivas " docker images -a " 

### Para borrar imagenes activas e inactivas " docker rmi ID-Imagen " ejemplo "docker rmi 2e5fjw"
### Para borrar contenedores activas e inactivas " docker rm ID-Contenedor " ejemplo "docker rm r2e5fjcew"