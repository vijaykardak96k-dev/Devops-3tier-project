from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
import os

app = Flask(__name__)
CORS(app)

def get_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST","db"),
        user=os.getenv("DB_USER","root"),
        password=os.getenv("DB_PASSWORD","root"),
        database=os.getenv("DB_NAME","devopsdb")
    )

@app.route("/")
def home():
    return """
    <h2>🚀 Vijay Kardak DevOps Backend</h2>
    <p>Available APIs:</p>
    <ul>
        <li>/api/add (POST)</li>
        <li>/api/visitors (GET)</li>
    </ul>
    """

@app.route("/api/add", methods=["POST"])
def add():

    data = request.json
    name = data["name"]
    age = data["age"]

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO visitors (name, age) VALUES (%s,%s)",
        (name, age)
    )

    conn.commit()

    return jsonify({"message":"Visitor added successfully"})


@app.route("/api/visitors")
def visitors():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM visitors")

    rows = cursor.fetchall()

    data = []

    for r in rows:
        data.append({
            "id": r[0],
            "name": r[1],
            "age": r[2]
        })

    return jsonify(data)


app.run(host="0.0.0.0", port=5000)
