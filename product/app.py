from dataclasses import dataclass
from flask import Flask, jsonify
from flask_restful import Resource, Api, abort, reqparse
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlite.db'
db = SQLAlchemy(app)


user_service_url = 'http://auth-service:5001'

@dataclass
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    title = db.Column(db.String(200))
    image = db.Column(db.String(200))
    likes = db.Column(db.Integer, default=0)


class Index(Resource):
    def get(self):
        return 'hello it is product page'


api.add_resource(Index, '/')


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
        id = request.json.get('id')
        title = request.json.get('title')
        image = request.json.get('image')
        likes = request.json.get('likes')

        if not title or not image:
            return {'error': 'title and image are required'}, 400

        new_product = Product(id=id, title=title, image=image, likes=likes)
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


api.add_resource(ProductResource, '/products')

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(port=5001, debug=True)
