from datetime import timedelta;

class Configuration ( ):
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:root@localhost:3307/authentication";
    JWT_SECRET_KEY = "JWT_SECRET_KEY"
    REDIS_HOST = "localhost"
