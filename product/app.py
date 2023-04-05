from dataclasses import dataclass
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlite.db'
db = SQLAlchemy(app)

user_service_url = 'http://localhost:5002'


@dataclass
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    image = db.Column(db.String(200))
    likes = db.Column(db.Integer, default=0)


class ProductResource(Resource):
    def get(self):
        products = Product.query.all()
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

    def post(self):
        data = request.get_json()
        title = data['title']
        image = data['image']
        likes = data['likes']

        if not title or not image:
            return jsonify({
                'error': 'title and image are required'
            })

        new_product = Product(title=title, image=image, likes=likes)
        db.session.add(new_product)
        db.session.commit()

        product_data = {
            'id': new_product.id,
            'title': new_product.title,
            'image': new_product.image,
            'likes': new_product.likes
        }
        requests.post(f'{user_service_url}/products', json=product_data)
        return product_data, 201


class LikesUpdateView(Resource):
    def put(self, id):
        req = requests.post(f'{user_service_url}/products/{id}/like')
        data = request.get_json()
        liked_prod = Product.query.filter_by(id=id).first()
        if not liked_prod:
            return jsonify({
                'message': 'Product not found'
            })
        liked_prod.likes = liked_prod.likes + 1
        db.session.commit()
        return jsonify({
            'message': 'your like is updated'
        })


api.add_resource(ProductResource, '/products')
api.add_resource(LikesUpdateView, '/products/<int:id>/like')

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(port=5001, debug=True)
