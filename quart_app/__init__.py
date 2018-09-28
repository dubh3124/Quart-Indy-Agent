import asyncio
import os
import logging
from quart import Quart
from logging.handlers import RotatingFileHandler
from quart_openapi import Pint
from indy import pool, ledger, wallet, did, crypto


def create_app():
    # maxBytes to small number, in order to demonstrate the generation of multiple log files (backupCount).
    handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=3)
    # getLogger(__name__):   decorators loggers to file + werkzeug loggers to stdout
    # getLogger('werkzeug'): decorators loggers to file + nothing to stdout
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.ERROR)
    logger.addHandler(handler)


    app = Quart(__name__)

    app.config.from_object('quart_app.config.Config')
    # app.logger.info("Config: %s" % app.config['ENVIRONMENT'])

    from logging.config import dictConfig



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