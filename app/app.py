from flask import Flask
from .cli import init_app as init_cli
from .models import db, Book, Audit, configure_listeners

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    db.init_app(app)

    configure_listeners(app)

    init_cli(app)

    return app
