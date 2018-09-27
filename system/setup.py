#! python3

"""
Used to setup the environment for heizung.

"""

from flask import Flask

from config import Config
import model

app = Flask('heizung')
app.secret_key = Config.secret_key
app.config['SQLALCHEMY_DATABASE_URI'] = Config.database_url
app.app_context()
app.app_context().push()

with app.app_context():
    model.db.init_app(app)

def setup_db():
    print("  Setting up database...")
    model.db.create_all()

def setup_systemd():
    print("  Setting up systemd-timers...")
    print("!!!!! TODO !!!!!")

if __name__ == '__main__':
    setup_db()
    setup_systemd()