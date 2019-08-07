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
        response[room.name] = [ms.serialize for ms in room.messages.all()]
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
    print(data)
    room = data['room']
    username = data['username']
    ms = data['message']
    m = Message(text=ms, user_name=username, room_id=Room.query.filter_by(name=room).first().id)
    db.session.add(m)
    db.session.commit()
    emit('recieve_message', m.jsonify(), room=room)


@socketio.on('get_messages')
def on_get_messages(data):
    username = data['username']
    rooms = User.query.filter_by(username=username).first().rooms

    response = {room.name: [ms.jsonify(username) for ms in room.messages.all()] for room in rooms}
    print(response)
    emit('send_messages', response)


@socketio.on('view')
def on_view(data):
    username = data['username']
    room = data['room']
    u = User.query.filter_by(username=username).first()
    u.view_room(room)
    