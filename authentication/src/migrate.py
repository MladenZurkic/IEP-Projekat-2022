from flask import Flask
from configuration import Configuration
from models import database, Role, UserRole, User
from flask_migrate import Migrate, init, migrate, upgrade
from sqlalchemy_utils import database_exists, create_database

app = Flask(__name__)
app.config.from_object(Configuration)

migrateObject = Migrate(app, database)


done = False

while not done:
    try:

        if (not database_exists(app.config["SQLALCHEMY_DATABASE_URI"])):
            create_database(app.config["SQLALCHEMY_DATABASE_URI"])

        database.init_app(app)

        with app.app_context() as context:
            init()
            migrate(message="Production migration")
            upgrade()

            warehouseRole = Role(name="warehouse")
            customerRole = Role(name="customer")
            adminRole = Role(name="admin")

            database.session.add(warehouseRole)
            database.session.add(customerRole)
            database.session.add(adminRole)
            database.session.commit()

            admin = User(
                email = "admin@admin.com",
                password = "1",
                forename = "admin",
                surname = "admin"
            )

            database.session.add(admin)
            database.session.commit()

            adminRoleUserRole = UserRole(
                userId=admin.id,
                roleId=adminRole.id
            )

            database.session.add(adminRoleUserRole)
            database.session.commit()

            done = True
    except Exception as error:
        print(error)