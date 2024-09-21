import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from daps_webui.config.config import Config

# all globals needs to be defined here
global_config = Config()
db = SQLAlchemy()

# define all loggers
daps_logger = logging.getLogger("daps")


def create_app() -> Flask:
    # init flask app
    app = Flask(__name__)
    app.config.from_object(global_config)

    # initiate logger(s)
    from daps_webui.utils.logger_utils import init_logger
    init_logger(daps_logger, global_config.logs, "daps_log.log", logging.INFO)

    # initiate database
    db.init_app(app)

    # import needed blueprints
    from daps_webui.views.home.home import home
    from daps_webui.views.settings.settings import settings
    from daps_webui.views.poster_renamer.poster_renamer import poster_renamer

    # register blueprints
    app.register_blueprint(home)
    app.register_blueprint(settings)
    app.register_blueprint(poster_renamer)
    
    return app

app = create_app()
with app.app_context():
    db.create_all()


# long jobs:
# import concurrent.futures
