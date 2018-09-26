import asyncio
import os
from quart import Quart
from quart_openapi import Pint
from logging.config import dictConfig
from indy import pool, ledger, wallet, did, crypto


def create_app():
    app = Quart(__name__)

    app.config.from_object('quart_app.config.Config')
    # app.logger.info("Config: %s" % app.config['ENVIRONMENT'])

    from logging.config import dictConfig

    dictConfig({
        'version': 1,
        'loggers': {
            'quart.app': {
                'level': 'DEBUG',
            },
        },
    })


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
    from quart_app.websocket.receive import websoc
    from quart_app.websocket.client import client
    app.register_blueprint(walletapi)
    app.register_blueprint(websoc)
    app.register_blueprint(client)
    #
    # # from flask_app.script import resetdb, populatedb
    # # # Click Commands
    # # app.cli
    # # app.cli.add_command(resetdb)
    # # app.cli.add_command(populatedb)
    #
    return app