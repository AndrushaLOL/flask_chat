from app import db
import operator as op

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
    messages = db.relationship('Message', backref='author', lazy='dynamic')
    viewed = db.Column(db.PickleType, default=dict)
    rooms = db.relationship('Room', secondary=association_table, backref='users')

    @property
    def _all_messages(self):
        res = {}
        for room in self.rooms:
            res[room.name] = list(map(op.attrgetter('id'), room.messages.all()))
        return res

    def view_room(self, room_name):
        if room_name not in self.viewed:
            self.viewed[room_name] = list()
        self.viewed[room_name].extend(self._all_messages[room_name])


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

    # users = db.relationship('User', secondary=association_table, backref='rooms')

    def __repr__(self):
        return f'<Room(name={self.name}>'


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, db.ForeignKey('user.username'))
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'))
    text = db.Column(db.String)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'room_id': self.room_id,
            'text': self.text
        }

    def jsonify(self, username):
        u = User.query.filter_by(username=username).first()
        viewed = self.id in u.viewed
        return {
            'text': self.text,
            'username': self.username,
            'viewed': viewed
        }

    def __repr__(self):
        return f'<Message(room_id={self.room_id}>'

