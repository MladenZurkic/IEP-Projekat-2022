import json
import datetime;
from configuration import Configuration
from roleCheckDecorator import roleCheck
from flask import Flask, request, Response
from flask_jwt_extended import JWTManager, jwt_required, get_jwt
from models import database, Product, Category, OrderProducts, Order, ProductCategories


app = Flask(__name__)
app.config.from_object(Configuration)

jwt = JWTManager(app)


@app.route("/search", methods=["GET"])
@jwt_required()
@roleCheck(role = "customer")
def search():
    category = request.args.get("category", "")
    name = request.args.get("name", "")


    categoriesDB = Category.query.filter(Category.name.like( f"%{category}%" )).all()

    productsDict = {}
    productsList = []
    categoriesList = []

    for category in categoriesDB:
        count = 0
        productCategories = ProductCategories.query.filter(ProductCategories.categoryId == category.id)

        for productCategory in productCategories:
            products = Product.query.filter(Product.id == productCategory.productId)

            for product in products:
                if name in product.name:
                    productTemp = {}
                    productTemp["id"] = product.id
                    productTemp["name"] = product.name
                    productTemp["price"] = product.price
                    productTemp["quantity"] = product.quantity
                    productTemp["categories"] = list(map(lambda x: x.name, product.categories))
                    productsDict[productTemp["id"]] = productTemp
                    count += 1
        if count:
            categoriesList.append(category.name)

    productsList = list(productsDict.values())

    return Response(json.dumps({"categories": categoriesList, "products": productsList }), status=200)


@app.route("/order", methods=["POST"])
@jwt_required()
@roleCheck(role = "customer")
def orderNow():
    requests = request.json.get("requests", "")

    requestsEmpty = len(requests) == 0
    if requestsEmpty:
        return Response(json.dumps({"message": "Field requests is missing."}), status=400)

    for index, requestedProduct in enumerate(requests):
        id = requestedProduct.get("id", "")
        quantity = requestedProduct.get("quantity", "")

        #quantityEmpty = len(quantity) == 0

        if not id:
            return Response(json.dumps({"message": "Product id is missing for request number " + str(index) + "."}), status=400)
        if not quantity:
            return Response(json.dumps({"message": "Product quantity is missing for request number " + str(index) + "."}), status=400)

        if not isinstance(id, int):
            return Response(json.dumps({"message": "Invalid product id for request number " + str(index) + "."}), status=400)
        if id <= 0:
            return Response(json.dumps({"message": "Invalid product id for request number " + str(index) + "."}), status=400)

        if not isinstance(quantity, int):
            return Response(json.dumps({"message": "Invalid product quantity for request number " + str(index) + "."}), status=400)
        if quantity <= 0:
            return Response(json.dumps({"message": "Invalid product quantity for request number " + str(index) + "."}), status=400)


        productExists = Product.query.filter(Product.id == id).first()
        if productExists is None:
            return Response(json.dumps({"message": "Invalid product for request number " + str(index) + "."}), status=400)

    claims = get_jwt()
    email = claims['sub']

    order = Order(userEmail = email, timestamp = datetime.datetime.now(), status = "PENDING")
    database.session.add(order)
    database.session.commit()



    for requested in requests:
        id = requested.get("id", "")
        quantity = requested.get("quantity", "")
        product = Product.query.filter(Product.id == id).first()
        productOrder = OrderProducts(orderId = order.id, productId = id, price = product.price, received = 0, requested = quantity)
        database.session.add(productOrder)

        if product.quantity >= productOrder.requested:
            orderStatus = True
            productOrder.received = productOrder.requested
            product.quantity -= productOrder.requested
        else:
            orderStatus = False
            productOrder.received = product.quantity
            product.quantity = 0


    if orderStatus:
        order.status = "COMPLETE"
    database.session.commit()

    return Response(json.dumps({"id": order.id}), status=200)



@app.route("/status", methods=["GET"])
@jwt_required()
@roleCheck(role = "customer")
def getStatus():
    claims = get_jwt()
    if "sub" in claims:
        email = claims["sub"]

        userOrders = Order.query.filter(Order.userEmail == email)
        orders = []

        for userOrder in userOrders:
            orderProducts = OrderProducts.query.filter(OrderProducts.orderId == userOrder.id)
            order= {}
            orderPrice = 0
            products= []

            for orderProduct in orderProducts:
                productCategories = ProductCategories.query.filter(ProductCategories.productId == orderProduct.productId)
                categories = []

                for productCategory in productCategories:
                    category = Category.query.filter(Category.id == productCategory.categoryId).first().name
                    categories.append(category)

                #jedan product
                product = {}
                product["categories"] = categories
                productDB = Product.query.filter(Product.id == productCategory.productId).first()
                product["name"] = productDB.name
                product["price"] = orderProduct.price
                product["received"] =  orderProduct.received
                product["requested"] =  orderProduct.requested
                orderPrice += orderProduct.requested * orderProduct.price
                products.append(product)

            #Jedan order
            order["products"] = products
            order["price"] = orderPrice
            order["status"] = userOrder.status
            order["timestamp"] = userOrder.timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
            orders.append(order)

        #Svi orderi
        return Response(json.dumps({"orders": orders}), status=200)

if (__name__ == "__main__"):
    database.init_app(app)
    app.run(debug=True, host="0.0.0.0", port=5002)
