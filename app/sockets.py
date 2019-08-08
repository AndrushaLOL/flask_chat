from app import socketio, db
from app.models import Message, Room, User
from flask_socketio import join_room, leave_room, send, emit


@socketio.on('connect')
def on_connect():
    # print(data)
    send('Connected!')


@socketio.on('initialize')
def on_initialize(data):
    username = data['username']
    u = User.query.filter_by(username=username).first()
    rooms = u.rooms
    response = {}
    for room in rooms:
        response[room.name] = {}
        try:
            ms = room.messages.all()[-1].serialize
        except:
            ms = {}
        response[room.name]['message'] = ms
        response[room.name]['count'] = len(u._all_messages.get(room.name, [])) - len(u.viewed.get(room.name, []))
        response[room.name]['users'] = [u.username for u in room.users if u.username != username] 

        join_room(room.name)
    emit('get_messages', response)
        

@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    send(f'{username} connected to the room.', room=room)


@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    send(f'{username} disconnected from the room.', room=room)


@socketio.on('create_room')
def on_create_room(data):
    room_name = data['room']
    users = data['users']
    us = []
    for u in users:
        user = User.query.filter_by(username=u).first()
        if user is None:
            send('Error')
            return
        us.append(user)
    r = Room(name=room_name)
    r.users.extend(us)

    db.session.add(r)
    db.session.commit()

    send(f'{r} created!')


@socketio.on('send_message')
def on_message(data):
    room = data.pop('room')
    data['room_id'] = Room.query.filter_by(name=room).first().id
    m = Message(**data)
    db.session.add(m)
    db.session.commit()


@socketio.on('view')
def on_view(data):
    username = data['username']
    room = data['room']
    u = User.query.filter_by(username=username).first()
    u.view_room(room)
    r = Room.query.filter_by(name=room).first()
    emit('room_message', [ms.serialize for ms in r.messages])
    