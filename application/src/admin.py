import json
from flask import Flask, Response
from configuration import Configuration
from roleCheckDecorator import roleCheck
from flask_jwt_extended import JWTManager, jwt_required
from models import database, Product, Category, OrderProducts, ProductCategories

app = Flask(__name__)
app.config.from_object(Configuration)

jwt = JWTManager(app)


@app.route("/productStatistics", methods=["GET"])
@jwt_required()
@roleCheck(role = "admin")
def getProductStatistics():
    allProducts = Product.query.all()
    statistics = []


    for product in allProducts:
        orderProducts = OrderProducts.query.filter(OrderProducts.productId == product.id)
        sold = 0
        waiting = 0

        for orderProduct in orderProducts:
            sold += orderProduct.requested
            waiting += orderProduct.requested - orderProduct.received
        oneStat = {}
        oneStat["name"] = product.name
        oneStat["sold"] = sold
        oneStat["waiting"] = waiting

        #test pada FIXED
        if sold > 0:
            statistics.append(oneStat)

    return Response(json.dumps({"statistics": statistics}), status=200)


@app.route("/categoryStatistics", methods=["GET"])
@jwt_required()
@roleCheck(role = "admin")
def getCategoryStatistics():
    allCategories = Category.query.all()
    categoriesList = []

    for category in allCategories:
        sum = 0
        productCategories = ProductCategories.query.filter(ProductCategories.categoryId == category.id)

        for productCategory in productCategories:
            products = Product.query.filter(Product.id == productCategory.productId)

            for product in products:
                orderProducts = OrderProducts.query.filter( OrderProducts.productId == product.id)

                for soldProduct in orderProducts:
                    sum += soldProduct.requested

        categoriesList.append({"sum": sum, "name": category.name})


    categoriesList.sort(key=lambda x: (-x["sum"], x["name"]), reverse=False)
    categoriesList = list(map(lambda x: x["name"], categoriesList))

    return Response(json.dumps({"statistics": categoriesList}), status=200)


if (__name__ == "__main__"):
    database.init_app(app)
    app.run(debug=True, host="0.0.0.0", port=5003)
