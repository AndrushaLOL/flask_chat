from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, index=True)
    phone = db.Column(db.String, unique=True, index=True)
    active = db.Column(db.Boolean, default=False, index=True)
    messages = db.relationship('Message', backref='author', lazy='dynamic')
    code = db.Column(db.Integer)

    def __repr__(self):
        return '<User(phone={})>'.format(self.phone)


class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, index=True)
    messages = db.relationship('Message', backref='room', lazy='dynamic')

    def __repr__(self):
        return f'<Room(name={self.name}>'


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    room_name = db.Column(db.String, db.ForeignKey('room.name'))
    text = db.Column(db.String)
    viewed = db.Column(db.PickleType)

    def __repr__(self):
        return f'<Message(user_id={self.user_id}, room_name={self.room_name})>'