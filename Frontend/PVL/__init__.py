from flask import Flask
import click
from flask.cli import with_appcontext
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


db = SQLAlchemy()
login_manager = LoginManager()
UPLOAD_FOLDER = '/home/VirtualLibrarian/Virtual-Librarian/Frontend/PVL/uploads'

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqldb://VirtualLibrarian:156156156Oi@VirtualLibrarian.mysql.pythonanywhere-services.com/VirtualLibrarian$site'
    #app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///VirtualLibrarian.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_POOL_TIMEOUT'] = 280
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['DEBUG'] = True
    app.secret_key = '123456'

    db.init_app(app)
    login_manager.init_app(app)

    app.cli.add_command(cm_db)

    with app.app_context():
        from . import routes

    return app

@click.command('cm-db')
@with_appcontext
def cm_db():
    from . import entidades
    db.create_all()
    print('Criado com sucesso')
