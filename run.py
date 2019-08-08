from app import app, socketio, db
from app.models import User, Message, Room
import random


def make_base_objects():
    u1 = User(username='Andrey', phone='123')
    u2 = User(username='Alsu', phone='1234')
    r = Room(name='test')
    u1.rooms.append(r)
    u2.rooms.append(r)
    for i in range(10):
        username = random.choice(['Andrey', 'Alsu'])
        m = Message(text=f'test_text{i}', username=username, room_id=r.id)
        db.session.add(m)
    db.session.add(u1)
    db.session.add(u2)
    db.session.add(r)
    db.session.commit()


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Message': Message, 'Room': Room, 'make_base_objects': make_base_objects}

if __name__ == '__main__':
    socketio.run(app, debug=True)