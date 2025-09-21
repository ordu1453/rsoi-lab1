from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
from models import db, Employee
import os

app = Flask(__name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(BASE_DIR, "employees.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

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

# ------------------- API -------------------

@app.route("/persons", methods=["GET"])
def get_all_persons():
    persons = Employee.query.all()
    return jsonify([
        {"id": p.id, "name": p.name, "address": p.address, "work": p.work, "age": p.age}
        for p in persons
    ])

@app.route("/persons/<int:personId>", methods=["GET"])
def get_person(personId):
    person = Employee.query.get(personId)
    if not person:
        abort(404, description="Person not found")
    return jsonify({
        "id": person.id,
        "name": person.name,
        "address": person.address,
        "work": person.work,
        "age": person.age
    })

@app.route("/persons", methods=["POST"])
def create_person():
    data = request.get_json()
    if not data or "name" not in data:
        abort(400, description="Name is required")

    new_person = Employee(
        name=data["name"],
        address=data.get("address"),
        work=data.get("work"),
        age=data.get("age", 18)
    )
    db.session.add(new_person)
    db.session.commit()

    return jsonify({"id": new_person.id}), 201

@app.route("/persons/<int:personId>", methods=["PATCH"])
def update_person(personId):
    person = Employee.query.get(personId)
    if not person:
        abort(404, description="Person not found")

    data = request.get_json()
    if not data:
        abort(400, description="No data provided")

    if "name" in data:
        person.name = data["name"]
    if "address" in data:
        person.address = data["address"]
    if "work" in data:
        person.work = data["work"]
    if "age" in data:
        person.age = data["age"]

    db.session.commit()
    return jsonify({"message": "Updated successfully"})

@app.route("/persons/<int:personId>", methods=["DELETE"])
def delete_person(personId):
    person = Employee.query.get(personId)
    if not person:
        abort(404, description="Person not found")

    db.session.delete(person)
    db.session.commit()
    return jsonify({"message": "Deleted successfully"})

@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Bad Request", "message": error.description}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not Found", "message": error.description}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal Server Error"}), 500


# ------------------- MAIN -------------------

if __name__ == "__main__":
    app.run(debug=True)
