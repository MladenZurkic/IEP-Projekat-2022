import json
import redis
from flask import Flask
from configuration import Configuration
from models import database, Product, Category, ProductCategories, OrderProducts, Order


app = Flask(__name__)
app.config.from_object(Configuration)

redis = redis.StrictRedis(Configuration.REDIS_HOST, 6379, charset="utf-8", decode_responses=True)


def user_counter():
    sub = redis.pubsub()
    sub.subscribe("products")

    for message in sub.listen():
        if message is not None and message["type"] == "message":
            data = json.loads(message["data"])
            categories = data["categories"]
            name = data["name"]
            quantity = int(data["quantity"])
            price = float(data["price"])
            productExists = Product.query.filter(Product.name == name).first()

            #Proizvod se ne nalazi u bazi
            if productExists is None:
                newProduct = Product(name=name, price=price, quantity=quantity)
                database.session.add(newProduct)
                database.session.commit()

                for category in categories:
                    categoryExists = Category.query.filter(
                        Category.name == category).first()
                    if categoryExists is None:
                        newCategory = Category(name=category)
                        database.session.add(newCategory)
                        database.session.commit()
                        newProductCategories = ProductCategories(
                            productId=newProduct.id, categoryId=newCategory.id)
                        database.session.add(newProductCategories)
                        database.session.commit()
                    else:
                        newProductCategories = ProductCategories(
                            productId=newProduct.id, categoryId=categoryExists.id)
                        database.session.add(newProductCategories)
                        database.session.commit()

            # Proizvod se nalazi u bazi
            else:
                flag = 0
                categoriesFromDB = ProductCategories.query.filter(
                    ProductCategories.productId == productExists.id)
                categoriesFromDBList = []

                #Pakovanje kategorije u listu radi lakseg poredjenja
                #FIX
                for category in categoriesFromDB:
                    existingCategory = Category.query.filter(
                        Category.id == category.categoryId).first()
                    if existingCategory is None:
                        flag = 1
                    else:
                        categoriesFromDBList.append(existingCategory.name)
                if not flag:
                    categories.sort()
                    categoriesFromDBList.sort()
                    if categories != categoriesFromDBList:
                        flag = 1
                    else:
                        # print(price update)
                        newPrice = (float(productExists.quantity * productExists.price +
                                    quantity * price).__round__(2) / float(productExists.quantity + quantity).__round__(2)).__round__(2)
                        productExists.quantity += quantity
                        productExists.price = newPrice
                        database.session.commit()

            # Provera da li neko ceka na ovaj proizvod

                ordersWithProduct = OrderProducts.query.filter(
                    OrderProducts.productId == productExists.id
                )

                if ordersWithProduct is not None:
                    ordersWithProduct.order_by(OrderProducts.id.asc())
                    for orderWithProduct in ordersWithProduct:
                        if productExists.quantity > 0:
                            if orderWithProduct.received != orderWithProduct.requested:
                                remaining = int(orderWithProduct.requested) - \
                                    int(orderWithProduct.received)
                                if remaining > productExists.quantity:
                                    orderWithProduct.received += productExists.quantity
                                    productExists.quantity = 0
                                else:
                                    productExists.quantity -= remaining
                                    orderWithProduct.received += remaining
                                    database.session.commit()
                                    order = Order.query.filter(
                                        Order.id == orderWithProduct.orderId).first()
                                    if order.status == "PENDING":
                                        ordersWithProductsForPendingOrder = OrderProducts.query.filter(
                                            OrderProducts.orderId == order.id)
                                        flag = 0
                                    for orderWithProduct in ordersWithProductsForPendingOrder:
                                        if orderWithProduct.received != orderWithProduct.requested:
                                            flag = 1
                                            # break
                                    if not flag:
                                        order.status = "COMPLETE"
                database.session.commit()


with app.app_context():
    while True:
        database.init_app(app)
        user_counter()
