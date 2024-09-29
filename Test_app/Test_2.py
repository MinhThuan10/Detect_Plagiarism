from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/test'
mongo = PyMongo(app)

@app.route('/')
def index():
    products = list(mongo.db.products.find())  # Chuyển đổi Cursor thành danh sách
    return render_template('index.html', products=products)


# Thêm endpoint cho AJAX
@app.route('/add_ajax', methods=['POST'])
def add_product_ajax():
    name = request.form.get('name')
    price = request.form.get('price')
    product_id = mongo.db.products.insert_one({'name': name, 'price': float(price)}).inserted_id
    product = mongo.db.products.find_one({'_id': product_id})
    return jsonify({'id': str(product['_id']), 'name': product['name'], 'price': product['price']})

@app.route('/delete/<product_id>', methods=['DELETE'])
def delete_product_ajax(product_id):
    mongo.db.products.delete_one({'_id': ObjectId(product_id)})
    return '', 204  # No Content

if __name__ == '__main__':
    app.run(debug=True)
