from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json
import os
import logging

# logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.secret_key = 'passwd123' #necesario para el carrito

DB_FILE = 'productos.json'

#Funciones auxiliares para cargar y guardar productos

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