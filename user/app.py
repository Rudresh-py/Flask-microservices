from dataclasses import dataclass
from flask import Flask, jsonify
from flask_restful import Resource, Api, abort, reqparse
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint
import requests

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlite.db'
db = SQLAlchemy(app)


@dataclass
class Products(db.Model):
    id: int
    title: str
    image: str

    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    title = db.Column(db.String(200))
    image = db.Column(db.String(200))


@dataclass
class ProductUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    product_id = db.Column(db.Integer)

    UniqueConstraint('user_id', 'product_id', name='user_product_unique')


class ProductResource(Resource):
    response = requests.get('http://localhost:5002/products')

    def get(self):
        products = Products.query.all()
        result = []
        for product in products:
            product_data = {
                'id': product.id,
                'title': product.title,
                'image': product.image,
                'likes': product.likes
            }
            result.append(product_data)
        return result


class ProductList(Resource):
    def get(self):
        return jsonify(Products.query.all())


api.add_resource(ProductList, '/products')


class LikeProducts(Resource):
    def get(self, id):
        req = requests.get('http://localhost:5001')
        json = req.json()

        try:
            productUser = ProductUser(user_id=json['id'], product_id=id)
            db.session.add(productUser)
            db.session.commit()

            # publish('product_liked', id)
        except:
            abort(400, 'You already liked this product')

        return jsonify({
            'message': 'success'
        })


api.add_resource(LikeProducts, '/products/<int:id>/like')

#
# @app.route('/products/<int:id>/like', methods=['POST'])
# def like(id):
#     req = requests.get('http://docker.for.mac.localhost:8000/api/user')
#     json = req.json()
#
#     try:
#         productUser = ProductUser(user_id=json['id'], product_id=id)
#         db.session.add(productUser)
#         db.session.commit()
#
#         # publish('product_liked', id)
#     except:
#         abort(400, 'You already liked this product')
#
#     return jsonify({
#         'message': 'success'
#     })


with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(port=5001, debug=True)
