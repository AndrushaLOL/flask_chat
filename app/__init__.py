from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from flask_restful import Api
from flask_socketio import SocketIO
from flask_moment import Moment
from flask_cors import CORS
from flask_login import LoginManager


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
api = Api(app)
socketio = SocketIO(app)
moment = Moment(app)
login = LoginManager(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


from app import routes, models, send_sms, sockets, resourses, login_utils