from flask_sqlalchemy import SQLAlchemy

database = SQLAlchemy()


class OrderProducts(database.Model):
    __tablename__ = "orderproducts"

    id = database.Column(database.Integer, primary_key=True)

    orderId = database.Column(database.Integer, database.ForeignKey("orders.id", ondelete="cascade"), nullable=False)

    productId = database.Column(database.Integer, database.ForeignKey("products.id", ondelete="cascade"), nullable=False)

    price = database.Column(database.Float, nullable=False)
    received = database.Column(database.Integer, nullable=False)
    requested = database.Column(database.Integer, nullable=False)


class ProductCategories(database.Model):
    __tablename__ = "productcategories"

    id = database.Column(database.Integer, primary_key=True)

    productId = database.Column(database.Integer, database.ForeignKey("products.id", ondelete="cascade"), nullable=False)
    categoryId = database.Column(database.Integer, database.ForeignKey("categories.id", ondelete="cascade"), nullable=False)


class Product(database.Model):
    __tablename__ = "products"

    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(256), nullable=False, unique=True)
    price = database.Column(database.Float(precision=2), nullable=False)
    quantity = database.Column(database.Integer, nullable=False)

    categories = database.relationship("Category", secondary=ProductCategories.__table__, back_populates="products")

    orders = database.relationship("Order", secondary=OrderProducts.__table__, back_populates="products")


class Order(database.Model):
    __tablename__ = "orders"

    id = database.Column(database.Integer, primary_key=True)
    userEmail = database.Column(database.String(256), nullable=False)
    timestamp = database.Column(database.DateTime, nullable=False)
    status = database.Column(database.String(256), nullable=False)

    products = database.relationship("Product", secondary=OrderProducts.__table__, back_populates="orders")


class Category(database.Model):
    __tablename__ = "categories"

    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(256), nullable=False)

    products = database.relationship(
        "Product", secondary=ProductCategories.__table__, back_populates="categories")
