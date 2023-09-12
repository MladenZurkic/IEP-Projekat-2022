import io
import csv
import json
import redis
from configuration import Configuration
from roleCheckDecorator import roleCheck
from flask import Flask, request, Response
from flask_jwt_extended import JWTManager, jwt_required


app = Flask(__name__)
app.config.from_object(Configuration)

jwt = JWTManager(app)
red = redis.StrictRedis(Configuration.REDIS_HOST, 6379, charset="utf-8", decode_responses=True)


@app.route("/update", methods=["POST"])
@jwt_required()
@roleCheck(role="warehouse")
def register():
    try:
        content = request.files["file"].stream.read().decode("utf-8")
    except:
        return Response(json.dumps({"message": "Field file is missing."}), status=400)


    stream = io.StringIO(content)
    reader = csv.reader(stream)

    for index, row in enumerate(reader):
        if len(row) != 4:
            return Response(json.dumps({"message": "Incorrect number of values on line " + str(index) + "."}), status=400)

        try:
            quantity = int(row[2])
        except:
            return Response(json.dumps({"message": "Incorrect quantity on line " + str(index) + "."}), status=400)
        if not quantity >= 0:
            return Response(json.dumps({"message": "Incorrect quantity on line " + str(index) + "."}), status=400)

        try:
            price = float(row[3])
        except:
            return Response(json.dumps({"message": "Incorrect price on line " + str(index) + "."}), status=400)
        if not price >= 0:
            return Response(json.dumps({"message": "Incorrect price on line " + str(index) + "."}), status=400)


    stream.seek(0)
    reader = csv.reader(stream)

    for row in reader:
        categories = row[0].split('|')
        name = row[1].replace('"', ' ').strip()
        quantity = row[2].strip()
        price = row[3].strip()

        red.publish('products', json.dumps({"categories": categories, "name": name, "quantity": quantity, "price": price}))

    return Response(status=200)


if (__name__ == "__main__"):
    app.run(debug=True, host="0.0.0.0", port=5001)
