from dataclasses import dataclass
from flask import Flask, jsonify, request, session
from flask_restful import Resource, Api, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint
import requests
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlite.db'
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = 'mysecretkey'

product_service_url = 'http://127.0.0.1:5001'


@dataclass
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)


@dataclass
class Products(db.Model):
    id: int
    title: str
    image: str

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    image = db.Column(db.String(200))


@dataclass
class ProductUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))

    UniqueConstraint('user_id', 'product_id', name='user_product_unique')


class RegisterApi(Resource):
    def post(self):
        # username = request.json.get('username')
        # password = request.json.get('password')
        data = request.get_json()
        username = data["username"]
        password = data["password"]
        if not username or not password:
            return jsonify(
                {'error': 'Username and password are required'})

        user = User(username=username,
                    password=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        return jsonify({'id': user.id, 'username': user.username, "message": "you are succucssfully created"})


# api.add_resource(RegisterApi, '/register')


#
#     return jsonify({'id': user.id, 'username': user.username}), 201

# @app.route('/register', methods=['POST'])
# def create_user():
#     username = request.json.get('username')
#     password = request.json.get('password')
#     if not username or not password:
#         return jsonify({'error': 'Username and password are required'}), 400
#
#     user = User(username=username, password=generate_password_hash(password))
#     db.session.add(user)
#     db.session.commit()
#
#     return jsonify({'id': user.id, 'username': user.username}), 201


class LoginApi(Resource):
    def post(self):
        # username = request.json.get('username')
        # password = request.json.get('password')
        data = request.get_json()
        username = data["username"]
        password = data["password"]
        if not username or not password:
            return jsonify(
                {'error': 'Username and password are required'})

        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password, password):
            return jsonify({'error': 'Invalid username or password'})

        session['user_id'] = user.id
        return jsonify({'id': user.id, 'username': user.username, "message": "you are succucssfully created"})


# api.add_resource(LoginApi, '/login')


#
# @app.route('/login', methods=['POST'])
# def login():
#     username = request.json.get('username')
#     password = request.json.get('password')
#     if not username or not password:
#         return jsonify({'error': 'Username and password are required'}), 400
#
#     user = User.query.filter_by(username=username).first()
#     if not user or not check_password_hash(user.password, password):
#         return jsonify({'error': 'Invalid username or password'}), 401
#
#     session['user_id'] = user.id
#     return jsonify({'id': user.id, 'username': user.username}), 200


class LogoutApi(Resource):
    def get(self):
        data = request.get_json()
        session["user_id"] = data["user_id"]
        if 'user_id' in session:
            session.pop('user_id', None)
            return jsonify({'message': 'Logged out successfully'})
        else:
            return jsonify({'error': 'User is not authenticated'})


# api.add_resource(LogoutApi, '/logout')


# @app.route('/logout')
# def logout():
#     if 'user_id' in session:
#         session.pop('user_id', None)
#         return jsonify({'message': 'Logged out successfully'}), 200
#     else:
#         return jsonify({'error': 'User is not authenticated'}), 401


class CreateProduct(Resource):
    def post(self):
        data = request.get_json()
        id = data['id']
        title = data['title']
        image = data['image']
        new_product = Products(id=id, title=title, image=image)
        db.session.add(new_product)
        db.session.commit()
        return jsonify({'status': 'success'})


# api.add_resource(CreateProduct, '/products')


# @app.route('/products', methods=['POST'])
# def create_product():
#     data = request.get_json()
#     id = data['id']
#     title = data['title']
#     image = data['image']
#     new_product = Products(id=id, title=title, image=image)
#     db.session.add(new_product)
#     db.session.commit()
#     return jsonify({'status': 'success'})


class LikeProducts(Resource):
    def get(self, id):
        # req = requests.get('http://localhost:5001/products')
        # json = req.json()

        try:
            if 'user_id' in session:
                productUser = ProductUser.query.filter_by(
                    user_id=session['user_id'], product_id=id).first()
                if not productUser:
                    productUser = ProductUser(user_id=session['user_id'],
                                              product_id=id)
                    db.session.add(productUser)
                    db.session.commit()
                else:
                    return jsonify({'error': 'you already liked this product'})
            else:
                return jsonify({'error': 'User is not authenticated'})
        except Exception as e:
            abort(400)
        product_user = {
            "id": productUser.id,
            "user_id": productUser.user_id,
            "product_id": productUser.product_id
        }
        requests.put(f'{product_service_url}/products/{id}/like',
                     json=product_user)
        return jsonify({
            'message': 'success your like is updated'
        })


api.add_resource(RegisterApi, '/register')
api.add_resource(LoginApi, '/login')
api.add_resource(LogoutApi, '/logout')
api.add_resource(CreateProduct, '/products')
api.add_resource(LikeProducts, '/products/<int:id>/like')

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(port=5002, debug=True)
