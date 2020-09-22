import os


class Config(object):
    SECRET_KEY = os.environ.get('SECRETKEY')
    DEBUG = True
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('POSTGRESQL') + 'coffee_shop'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    # SECRET_KEY = 'development'
    SQLALCHEMY_ECHO = True


# class ProductionConfig(Config):
#     DATABASE_URI = 'mysql://user@localhost/foo'

class TestingConfig(Config):
    # SECRET_KEY = 'testmyplantapp'
    TESTING = True


configs = {
    'development': DevelopmentConfig,
    'testing': TestingConfig
}
