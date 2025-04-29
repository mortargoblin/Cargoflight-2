# backend.py

from flask import Flask, request, Response
import mysql.connector

app = Flask(__name__)
@app.route("blahblah")


if __name__ == "__main__":
    app.run(use_reloader=True, host="127.0.0.1", port=3000)
