# from flask import Flask, render_template, request, redirect, url_for, session, jsonify
# import json
# import os
# import logging

# from werkzeug.utils import secure_filename
# from datetime import datetime

# # logging.basicConfig(level=logging.INFO)

# app = Flask(__name__)
# app.secret_key = 'passwd123' #necesario para el carrito

# DB_FILE = 'productos.json'


from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json
import os
import logging
import base64
import requests
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'passwd123'  # necesario para el carrito

# Configuración GitHub
GITHUB_REPO = "JulianValencia96/catalogo_accesorios"  # Cambiar por tu usuario/repo
GITHUB_BRANCH = "main"  # Rama donde está el JSON
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # Configurar en Render
DB_FILE = 'productos.json'

# ... (conserva tus configuraciones de imágenes y funciones auxiliares existentes) ...

def cargar_productos():
    # Si estamos en Render, usa GitHub API
    if os.getenv("RENDER"):  # Variable de entorno que existe en Render
        return cargar_desde_github()
    else:  # Modo local
        if not os.path.exists(DB_FILE):
            with open(DB_FILE, 'w') as f:
                json.dump([], f)
        with open(DB_FILE, 'r') as f:
            return json.load(f)

def guardar_productos(productos):
    if os.getenv("RENDER"):
        guardar_en_github(productos)
    else:
        with open(DB_FILE, 'w') as f:
            json.dump(productos, f, indent=4)

def cargar_desde_github():
    try:
        url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{DB_FILE}?ref={GITHUB_BRANCH}"
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        file_data = response.json()
        return json.loads(base64.b64decode(file_data["content"]).decode("utf-8"))
    except Exception as e:
        print(f"Error al cargar desde GitHub: {str(e)}")
        return []

def guardar_en_github(productos):
    try:
        # 1. Obtener el SHA del archivo actual
        url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{DB_FILE}?ref={GITHUB_BRANCH}"
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        response = requests.get(url, headers=headers)
        file_data = response.json()

        # 2. Subir cambios
        commit_data = {
            "message": "Actualización automática de productos",
            "content": base64.b64encode(json.dumps(productos, indent=4).encode("utf-8")).decode("utf-8"),
            "sha": file_data["sha"]
        }
        update_response = requests.put(url, headers=headers, json=commit_data)
        update_response.raise_for_status()
    except Exception as e:
        print(f"Error al guardar en GitHub: {str(e)}")
        raise



#Funciones auxiliares para cargar y guardar productos


#Imagenes ----------------------

# Configuración
app.config['UPLOAD_FOLDER'] = 'static/img'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB máximo

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/cargarImgs')
def imgSubidas():
    # Obtener lista de imágenes existentes
    images = []
    if os.path.exists(app.config['UPLOAD_FOLDER']):
        images = [img for img in os.listdir(app.config['UPLOAD_FOLDER']) 
                 if img.lower().endswith(tuple(app.config['ALLOWED_EXTENSIONS']))]
    return render_template('cargaImgs.html', images=images)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'files[]' not in request.files:
        return redirect(request.url)
    
    files = request.files.getlist('files[]')
    success_count = 0
    
    for file in files:
        if file.filename == '':
            continue
            
        if file and allowed_file(file.filename):
            try:
                # Generar nombre único
                filename = secure_filename(file.filename)
                # unique_name = f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                success_count += 1
            except Exception as e:
                print(f"Error al subir {file.filename}: {str(e)}")
    
    return redirect(url_for('imgSubidas'))







def cargar_productos():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w') as f:
            json.dump([], f)
    with open(DB_FILE, 'r') as f:
        return json.load(f)

def guardar_productos(productos):
    with open(DB_FILE, 'w') as f:
        json.dump(productos, f, indent=4)

def leer_productos():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            return json.load(f)
        return[]

def escribir_productos(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/')
def index():
    productos = cargar_productos()
    return render_template('index.html', productos=productos)

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/api/productos', methods=['GET'])
def get_productos():
    return jsonify(leer_productos())

@app.route('/api/productos/<int:id>', methods=['DELETE'])
def eliminar_producto(id):
    productos = leer_productos()
    productos = [p for p in productos if p['id'] != id]
    escribir_productos(productos)
    return jsonify({"message": "Producto eliminado"}), 200

@app.route('/api/productos', methods=['POST'])
def agregar_producto():
    productos = leer_productos()
    nuevo = request.json
    nuevo['id'] = max([p['id'] for p in productos], default=0) +1 #id automatico - evalua el id maximo y suma 1 al proximo registro
    productos.append(nuevo)
    escribir_productos(productos)
    return jsonify(nuevo), 201

@app.route('/api/productos/<int:id>', methods = ['PUT'])
def editar_productos(id):
    productos = leer_productos()
    for p in productos:
        if p['id'] == id:
            # logging.info("Registro identificado:" + p['nombre'])
            # logging.info("Registro identificado:" + p['precio'])
            p.update(request.json)
            escribir_productos(productos)
            return jsonify(p)
    return jsonify({"error": "Producto no encontrado"}), 404

if __name__ == '__main__':
    app.run(debug= True)