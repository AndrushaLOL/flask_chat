import operator as op
import datetime
from hashlib import md5

import jwt
from sqlalchemy.sql import func
from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from app import db, login, app


association_table = db.Table(
    'association',
    db.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('room_id', db.Integer, db.ForeignKey('room.id'))
)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, index=True)
    email = db.Column(db.String, unique=True, index=True)
    active = db.Column(db.Boolean, default=False)
    messages = db.relationship('Message', backref='user', lazy='dynamic')
    password_hash = db.Column(db.String(128))
    viewed = db.Column(db.PickleType, default=dict, nullable=False)
    rooms = db.relationship('Room', secondary=association_table, backref='users')
    photo_url = db.Column(db.String)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def add_room(self, room):
        self.rooms.append(room)

    def del_room(self, room):
        self.rooms.remove(room)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @hybrid_property
    def contacts(self):
        return [room.name for room in self.rooms]

    def encode_auth_token(self):
        """
        Generates auth token
        :return: string
        """
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1),
                'iat': datetime.datetime.utcnow(),
                'sub': self.id
            }
            return jwt.encode(payload, app.config.get('SECRET_KEY'), algorithm='HS256')
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        """
        Decode auth token
        :param auth_token:
        :return: string|integer
        """
        try:
            payload = jwt.decode(auth_token, app.config.get('SECRET_KEY'))
            return int(payload['sub'])
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again'


    @property
    def _all_messages(self):
        res = {}
        for room in self.rooms:
            res[room.name] = list(map(op.attrgetter('id'), room.messages.all()))
        return res

    def view_room(self, room_name):
        viewed = self.viewed.copy()
        if room_name not in viewed:
            viewed[room_name] = list()

        viewed[room_name] = self._all_messages[room_name]

        self.viewed = viewed
        db.session.commit()


    def __repr__(self):
        return '<User(username={})>'.format(self.username)


class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, index=True)
    messages = db.relationship('Message', backref='room', lazy='dynamic')

    @property
    def type(self):
        if len(self.users) > 2:
            return 'group'
        else:
            return 'dialog'

    def __repr__(self):
        s = f"""
        name: {self.name}
        users: {[u.username for u in self.users]}
        messages: {self.messages.all()}
        """
        return s


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, db.ForeignKey('user.username'))
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'))
    text = db.Column(db.String)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'roomname': self.room.name,
            'text': self.text,
            'username': self.username,
            'time': str(self.created_at)
        }


    def __repr__(self):
        return f'<Message(room_name={self.room.name}>'








