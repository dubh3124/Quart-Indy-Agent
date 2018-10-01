import asyncio
import os
import logging
from quart import Quart
from quart.logging import default_handler
from logging.handlers import RotatingFileHandler
from logging.config import dictConfig
from quart_openapi import Pint
from indy import pool, ledger, wallet, did, crypto


def create_app():
    logging.basicConfig(level=logging.DEBUG)

    # dictConfig({
    #     'version': 1,
    #     'formatters': {
    #         'verbose': {
    #             'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
    #         },
    #         'simple': {
    #             'format': '%(levelname)s %(message)s'
    #         },
    #     },
    #     'handlers': {
    #         'default': {
    #             'level': 'INFO',
    #             'formatter': 'verbose',
    #             'class': 'logging.StreamHandler',
    #         },
    #     },
    #     'loggers': {
    #         'quart.serving': {
    #             'handlers': ['default'],
    #             'level': 'INFO',
    #         },
    #         '__name__': {
    #             'handlers': ['default'],
    #             'level': 'DEBUG',
    #         },
    #         'asyncio': {
    #             'handlers': ['default'],
    #             'level': 'DEBUG',
    #         }
    #     },
    # })

    app = Quart(__name__)

    app.config.from_object("quart_app.config.Config")
    # app.logger.info("Config: %s" % app.config['ENVIRONMENT'])

    # #  Logging
    # import logging
    # logging.basicConfig(
    #     level='DEBUG',
    #     format='%(asctime)s %(levelname)s: %(message)s '
    #            '[in %(pathname)s:%(lineno)d]',
    #     datefmt='%Y%m%d-%H:%M%p',
    # )

    # from flask_app.apiv1.auth import jwt
    # jwt.init_app(app)
    #
    # # CORS
    # from flask_cors import CORS
    # CORS(app, supports_credentials=True)
    #
    # # Email
    # from flask_mail import Mail
    # app.mail = Mail(app)
    #
    # # MongoEngine
    # from flask_app.db_init import db
    # app.db = db
    # app.db.init_app(app)
    #
    # Business Logic
    # http://flask.pocoo.org/docs/patterns/packages/
    # http://flask.pocoo.org/docs/blueprints/
    from quart_app.apis.wallet import walletapi
    from quart_app.apis.main import main
    from quart_app.websocket.receive import websoc

    app.register_blueprint(main)
    app.register_blueprint(walletapi)
    app.register_blueprint(websoc)
    #
    # # from flask_app.script import resetdb, populatedb
    # # # Click Commands
    # # app.cli
    # # app.cli.add_command(resetdb)
    # # app.cli.add_command(populatedb)
    #
    return app
