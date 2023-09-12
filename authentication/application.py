import json
import re
from flask import request, Response, jsonify
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity, \
    get_jwt
from sqlalchemy import and_
from settings import application, database
from models import User, UserRole
from adminDecorator import roleCheck


jwt = JWTManager ( application );

@application.route("/register", methods=["POST"])
def register():
    email = request.json.get("email", "")
    password = request.json.get("password", "");
    forename = request.json.get("forename", "");
    surname = request.json.get("surname", "");
    isCustomer = request.json.get("isCustomer", "")

    emailEmpty = len(email) == 0;
    passwordEmpty = len(password) == 0
    forenameEmpty = len(forename) == 0
    surnameEmpty = len(surname) == 0
    isCustomerEmpty = 1

    if isCustomer == True or isCustomer == False:
        isCustomerEmpty = 0
    if forenameEmpty:
        return Response(json.dumps({"message": "Field forename is missing."}), status=400)
    if surnameEmpty:
        return Response(json.dumps({"message": "Field surname is missing."}), status=400)
    if emailEmpty:
        return Response(json.dumps({"message": "Field email is missing."}), status = 400)
    if passwordEmpty:
        return Response(json.dumps({"message": "Field password is missing."}), status=400)
    if isCustomerEmpty:
        return Response(json.dumps({"message": "Field isCustomer is missing."}), status = 400)

    pat = "^[a-zA-Z0-9-_]+@[a-zA-Z0-9]+\.[a-z]{2,3}$"
    if not re.match(pat,email):
        return Response(json.dumps({"message": "Invalid email."}), status=400)

    if len(password) < 8:
        return Response(json.dumps({"message": "Invalid password."}), status=400)
    if re.search("[0-9]", password) is None:
        return Response(json.dumps({"message": "Invalid password."}), status=400)
    if re.search("[a-z]", password) is None:
        return Response(json.dumps({"message": "Invalid password."}), status=400)
    if re.search("[A-Z]", password) is None:
        return Response(json.dumps({"message": "Invalid password."}), status=400)

    userExists = User.query.filter( User.email == email).first()

    if userExists is not None:
        return Response(json.dumps({"message": "Email already exists."}), status=400)

    user = User(email = email, forename=forename, surname=surname, password=password)

    database.session.add ( user )
    database.session.commit ( )

    if isCustomer:
        roleId = 1
    else:
        roleId = 2

    userRole = UserRole(userId = user.id, roleId = roleId)
    database.session.add(userRole)
    database.session.commit()

    return Response(status=200)

@application.route("/login", methods=["POST"])
def login():
    email = request.json.get("email", "")
    password = request.json.get("password", "")

    emailEmpty = len(email) == 0
    passwordEmpty = len(password) == 0

    if emailEmpty:
        return Response(json.dumps({"message": "Field email is missing."}), status=400)
    if passwordEmpty:
        return Response(json.dumps({"message": "Field password is missing."}), status=400)

    pat = "^[a-zA-Z0-9-_]+@[a-zA-Z0-9]+\.[a-z]{2,3}$"
    if not re.match(pat, email):
        return Response(json.dumps({"message": "Invalid email."}), status=400)

    user = User.query.filter(and_(User.email == email, User.password == password)).first();

    if (not user):
        return Response(json.dumps({"message": "Invalid credentials."}), status=400)

    additionalClaims = {
        "forename" : user.forename,
        "surname" : user.surname,
        "roles" : [ str ( role ) for role in user.roles ]
    }

    accessToken = create_access_token(identity=user.email, additional_claims=additionalClaims);
    refreshToken = create_refresh_token(identity=user.email, additional_claims=additionalClaims);

    return jsonify(accessToken = accessToken, refreshToken = refreshToken),200


@application.route("/refresh", methods=["POST"])
@jwt_required( refresh=True )
def refreshToken():
    identity = get_jwt_identity()
    refreshClaims = get_jwt()

    additionalClaims = {
        "forename" : refreshClaims["forename"],
        "surname": refreshClaims["surname"],
        "roles": refreshClaims["roles"]
    }

    return jsonify(accessToken = create_access_token(identity = identity, additional_claims=additionalClaims)),200


@application.route("/delete", methods=["POST"])
@jwt_required()
@roleCheck( role = "admin")
def deleteUser():
    email = request.json.get("email", "")

    emailEmpty = len(email) == 0

    if emailEmpty:
        return Response(json.dumps({"message": "Field email is missing."}), status=400)

    pat = "^[a-zA-Z0-9-_]+@[a-zA-Z0-9]+\.[a-z]{2,3}$"
    if not re.match(pat, email):
        return Response(json.dumps({"message": "Invalid email."}), status=400)

    userDelete = User.query.filter(and_(User.email == email)).first();

    if (not userDelete):
        return Response(json.dumps({"message": "Unknown user."}), status=400)

    database.session.delete(userDelete)
    database.session.commit()

    return Response(status=200)

if ( __name__ == "__main__" ):
    database.init_app ( application );
    application.run ( debug = True, port = 5002 );