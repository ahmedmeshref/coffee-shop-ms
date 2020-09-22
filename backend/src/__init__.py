from flask import Flask

from config import config_by_name


def create_app(config_object='development'):
    # create and configure the app
    app = Flask(__name__)
    # app.config.from_object(config_by_name[config_object])

    with app.app_context():
        setup_db(app)
        # import blueprints

        return app
