from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from configuration import Configuration

application = Flask ( __name__ );
application.config.from_object ( Configuration );

database = SQLAlchemy ( );