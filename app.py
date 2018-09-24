from flask import Flask, render_template, g
from model import db, User
from config import Config

app = Flask('heizung')
app.config['SQLALCHEMY_DATABASE_URI'] = Config.database_url
db.init_app(app)

@app.route('/')
def hello_world():
    return render_template('dashboard.html')

@app.route('/init/')
def init():
    db.create_all()
    return "a"


if __name__ == '__main__':
    app.run()
