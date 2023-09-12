from flask_jwt_extended import JWTManager
from application.settings import application, database

jwt = JWTManager ( application );



if ( __name__ == "__main__" ):
    database.init_app ( application );
    application.run ( debug = True, port = 5002 );