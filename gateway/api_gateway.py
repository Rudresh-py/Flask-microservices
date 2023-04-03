from flask import Flask, jsonify
import requests

app = Flask(__name__)


@app.route('/')
def home():
    return 'API Gateway'


@app.route('/users')
def get_users():
    response = requests.get('http://localhost:5002')
    return jsonify(response.text)


@app.route('/products')
def get_products():
    response = requests.get('http://localhost:5001')
    return jsonify(response.text)


if __name__ == "__main__":
    app.run(port=5000, debug=True)