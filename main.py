from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from flask_cors import CORS


# Configuración
app = Flask(__name__)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'biblioteca.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
CORS(app)

# Modelo
class Libro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(255), nullable=False)
    autor = db.Column(db.String(255), nullable=False)
    isbn = db.Column(db.String(13), unique=True, nullable=False)
    categoria = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.String(50), nullable=False, default='disponible')
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

# Crear base de datos
with app.app_context():
    db.create_all()

# Rutas
@app.route("/libros", methods=["GET"])
def listar_libros():
    libros = Libro.query.all()
    return jsonify([libro_to_dict(libro) for libro in libros])

@app.route("/libros/<int:id>", methods=["GET"])
def obtener_libro(id):
    libro = Libro.query.get_or_404(id)
    return jsonify(libro_to_dict(libro))

@app.route("/libros", methods=["POST"])
def crear_libro():
    data = request.get_json()
    if not data:
        abort(400, description="Datos inválidos")
    try:
        nuevo_libro = Libro(**data)
        db.session.add(nuevo_libro)
        db.session.commit()
        return jsonify({"mensaje": "Libro creado correctamente"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@app.route("/libros/<int:id>", methods=["PUT"])
def actualizar_libro(id):
    libro = Libro.query.get_or_404(id)
    data = request.get_json()
    if not data:
        abort(400, description="Datos inválidos")
    for key, value in data.items():
        if hasattr(libro, key):
            setattr(libro, key, value)
    db.session.commit()
    return jsonify({"mensaje": "Libro actualizado correctamente"})

@app.route("/libros/<int:id>", methods=["DELETE"])
def eliminar_libro(id):
    libro = Libro.query.get_or_404(id)
    db.session.delete(libro)
    db.session.commit()
    return jsonify({"mensaje": "Libro eliminado correctamente"})

@app.route("/libros/buscar", methods=["GET"])
def buscar_libros():
    titulo = request.args.get("titulo")
    autor = request.args.get("autor")
    categoria = request.args.get("categoria")

    query = Libro.query
    if titulo:
        query = query.filter(Libro.titulo.ilike(f"%{titulo}%"))
    if autor:
        query = query.filter(Libro.autor.ilike(f"%{autor}%"))
    if categoria:
        query = query.filter(Libro.categoria.ilike(f"%{categoria}%"))

    libros = query.all()
    return jsonify([libro_to_dict(libro) for libro in libros])

# Función auxiliar
def libro_to_dict(libro):
    return {
        "id": libro.id,
        "titulo": libro.titulo,
        "autor": libro.autor,
        "isbn": libro.isbn,
        "categoria": libro.categoria,
        "estado": libro.estado,
        "fecha_creacion": libro.fecha_creacion.isoformat()
    }

# Ejecutar la app
if __name__ == "__main__":
    app.run(debug=True)
