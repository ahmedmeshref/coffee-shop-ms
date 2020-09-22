from flask import Flask

from config import configs


def create_app(config_object='development'):
    # create and configure the app
    app = Flask(__name__)
    app.config.from_object(configs[config_object])

    with app.app_context():
        # setup_db(app)
        # import blueprints

        return app
