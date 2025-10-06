from flask import Flask, render_template, request, redirect, url_for, jsonify
from models import db, Employee
import os

app = Flask(__name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(BASE_DIR, "employees.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

db.init_app(app)

with app.app_context():
    db.create_all()

# ------------------- ВЕБ-ИНТЕРФЕЙС -------------------

@app.route("/")
def index():
    employees = Employee.query.all()
    return render_template("index.html", employees=employees)

@app.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        name = request.form["name"]
        address = request.form["address"]
        work = request.form["work"]
        age = request.form["age"]

        new_emp = Employee(name=name, address=address, work=work, age=age)
        db.session.add(new_emp)
        db.session.commit()

        return redirect(url_for("index"))
    return render_template("create.html")

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    emp = Employee.query.get_or_404(id)
    if request.method == "POST":
        emp.name = request.form["name"]
        emp.address = request.form["address"]
        emp.work = request.form["work"]
        emp.age = request.form["age"]

        db.session.commit()
        return redirect(url_for("index"))
    return render_template("edit.html", emp=emp)

@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    emp = Employee.query.get_or_404(id)
    db.session.delete(emp)
    db.session.commit()
    return redirect(url_for("index"))

# ------------------- API (OpenAPI person-service.yaml) -------------------

@app.route("/api/v1/persons", methods=["GET"])
def list_persons():
    persons = Employee.query.all()
    return jsonify([
        {
            "id": p.id,
            "name": p.name,
            "address": p.address,
            "work": p.work,
            "age": p.age
        } for p in persons
    ]), 200


@app.route("/api/v1/persons/<int:id>", methods=["GET"])
def get_person(id):
    person = Employee.query.get(id)
    if not person:
        return jsonify({"message": f"Person with id={id} not found"}), 404

    return jsonify({
        "id": person.id,
        "name": person.name,
        "address": person.address,
        "work": person.work,
        "age": person.age
    }), 200


@app.route("/api/v1/persons", methods=["POST"])
def create_person():
    data = request.get_json()
    if not data or "name" not in data:
        return jsonify({
            "message": "Validation error",
            "errors": {"name": "Name is required"}
        }), 400

    new_person = Employee(
        name=data["name"],
        address=data.get("address"),
        work=data.get("work"),
        age=data.get("age", 18)
    )
    db.session.add(new_person)
    db.session.commit()

    location_url = url_for("get_person", id=new_person.id, _external=True)
    response = jsonify({
        # "id": new_person.id,
        # "name": new_person.name,
        # "address": new_person.address,
        # "work": new_person.work,
        # "age": new_person.age
    })
    response.status_code = 201
    response.headers["Location"] = location_url
    return response


@app.route("/api/v1/persons/<int:id>", methods=["PATCH"])
def update_person(id):
    person = Employee.query.get(id)
    if not person:
        return jsonify({"message": f"Person with id={id} not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({
            "message": "Validation error",
            "errors": {"body": "No data provided"}
        }), 400

    if "name" in data:
        person.name = data["name"]
    if "address" in data:
        person.address = data["address"]
    if "work" in data:
        person.work = data["work"]
    if "age" in data:
        person.age = data["age"]

    db.session.commit()

    return jsonify({
        "id": person.id,
        "name": person.name,
        "address": person.address,
        "work": person.work,
        "age": person.age
    }), 200


@app.route("/api/v1/persons/<int:id>", methods=["DELETE"])
def delete_person(id):
    person = Employee.query.get(id)
    if not person:
        return jsonify({"message": f"Person with id={id} not found"}), 404

    db.session.delete(person)
    db.session.commit()
    return "", 204


# ------------------- ERROR HANDLERS -------------------

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "message": "Bad Request",
        "errors": {"error": error.description if hasattr(error, "description") else "Invalid request"}
    }), 400


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "message": error.description if hasattr(error, "description") else "Resource not found"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"message": "Internal Server Error"}), 500


# ------------------- MAIN -------------------

if __name__ == "__main__":
    app.run(debug=True, port=8080)
