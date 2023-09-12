import os

databaseUrl = os.environ.get("DATABASE_URL")

class Configuration ():
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@{databaseUrl}:3306/store"
    JWT_SECRET_KEY = "JWT_SECRET_KEY"
    REDIS_HOST = "redis"
