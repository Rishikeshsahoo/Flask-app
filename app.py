from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from config import Config

# Initialize the Flask app and SQLAlchemy
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

username="admin"

# Define the Product model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    stock_level = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Product {self.name}>'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False,unique=True)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)


    def __repr__(self):
        return f'<User {self.username}:{self.email}>'

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    username= db.Column(db.String(100), db.ForeignKey('user.username'), nullable=False)
    product = db.relationship('Product', backref=db.backref('orders', lazy=True))
    user = db.relationship('User', backref=db.backref('orders', lazy=True))


    def __repr__(self):
        return f'<Order {self.id}>'
    
with app.app_context():
    db.create_all()

@app.route('/products', methods=['POST'])
def create_product():
    data = request.get_json()
    new_product = Product(name=data['name'], stock_level=data['stock_level'])

    db.session.add(new_product)
    db.session.commit()

    return jsonify({'message': 'Product created!'}), 201

@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    allProducts=[]
    for product in products:
        allProducts.append(
            {
                'id':product.id,
                'name':product.name,
                'stock_available':product.stock_level
            }
        )
    return jsonify(allProducts), 200

@app.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    data = request.get_json()
    product = Product.query.get_or_404(id)
    product.stock_level = data['stock_level']

    db.session.commit()
    return jsonify({'message': 'Product updated!'}), 200

@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()

    return jsonify({'message': 'Product deleted!'}), 200

@app.route('/orders', methods=['POST'])
def place_order():
    data = request.get_json()
    product = Product.query.get_or_404(data['product_id'])
    user = User.query.get_or_404(data['product_id'])


    if product.stock_level < data['quantity']:
        return jsonify({'message': 'Insufficient stock!'}), 400

    new_order = Order(product_id=product.id, quantity=data['quantity'],username=user.username)
    product.stock_level -= data['quantity']  # Update stock level

    db.session.add(new_order)
    db.session.commit()

    return jsonify({'message': 'Order placed!'}), 201

@app.route('/orders', methods=['GET'])
def get_orders():
    orders = Order.query.all()

    return jsonify([{'id': order.id, 'product_id': order.product_id, 'quantity': order.quantity,'username':order.username}  for order in orders]), 200

@app.route("/users", methods=["POST"])
def add_user():
    data = request.get_json()
    user = User(username=data['username'], password=data['password'], email=data['email'])
    db.session.add(user)
    db.session.commit()

    return jsonify({'message':"user added"})

@app.route("/users", methods=["GET"])
def get_user():
    users = User.query.all()
    allUsers=[]
    for user in users:
        allUsers.append(
            {'id': user.id, 'username': user.username, 'password': user.password}
        )
    return jsonify(allUsers), 200


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
