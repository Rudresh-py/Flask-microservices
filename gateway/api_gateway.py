from flask import Flask, jsonify, request, session
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mygatewaysecretkey'


user_service_url = 'http://127.0.0.1:5002'
product_service_url = 'http://127.0.0.1:5001'


@app.route('/')
def home():
    return 'API Gateway'


@app.route('/products', methods=['GET'])
def get_products():
    response = requests.get(f'{product_service_url}/products')
    data = response.json()
    return jsonify(data)


@app.route('/products', methods=['POST'])
def create_products():
    # data = requests.json
    new_product = {
        "title": request.json.get('title'),
        "image": request.json.get('image'),
        "likes": request.json.get('likes')
    }
    response = requests.post(f'{product_service_url}/products',
                             json=new_product)
    data = response.json()
    return jsonify(data)


@app.route('/register', methods=['POST'])
def register():
    new_user = {
        "username": request.json.get('username'),
        "password": request.json.get('password')
    }

    response = requests.post(f'{user_service_url}/register', json=new_user)
    data = response.json()
    return jsonify(data)


@app.route('/login', methods=['POST'])
def login():
    login_user = {
        "username": request.json.get('username'),
        "password": request.json.get('password')
    }
    response = requests.post(f'{user_service_url}/login', json=login_user)
    data = response.json()
    session['user_id'] = data['id']
    return jsonify(data)


@app.route('/logout', methods=['GET'])
def logout():
    try:
        user_id = {
            "user_id": session["user_id"]
            }
        response = requests.get(f'{user_service_url}/logout', json=user_id)
        session.pop('user_id', None)
        data = response.json()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': 'User is not authenticated'})


@app.route('/products/<int:id>/like', methods=['GET'])
def like_products(id):
    try:
        user_id = {
            "user_id": session["user_id"]
            }
        response = requests.get(f'{user_service_url}/products/{id}/like',
                                json=user_id)
        data = response.json()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': 'User is not authenticated'})


if __name__ == "__main__":
    app.run(port=5000, debug=True)
