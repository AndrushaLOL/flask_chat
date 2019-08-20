from app import db
import operator as op
import datetime
from sqlalchemy.sql import func
from sqlalchemy.ext.hybrid import hybrid_property

association_table = db.Table(
    'association',
    db.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('room_id', db.Integer, db.ForeignKey('room.id'))
)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, index=True)
    phone = db.Column(db.String, unique=True, index=True)
    active = db.Column(db.Boolean, default=False)
    messages = db.relationship('Message', backref='user', lazy='dynamic')
    viewed = db.Column(db.PickleType, default=dict, nullable=False)
    rooms = db.relationship('Room', secondary=association_table, backref='users')

    @hybrid_property
    def contacts(self):
        return [room.name for room in self.rooms]

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
        return '<User(phone={})>'.format(self.phone)


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

