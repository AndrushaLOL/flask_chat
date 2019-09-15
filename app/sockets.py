from functools import wraps
import datetime

from flask_socketio import join_room, leave_room, send, emit, disconnect
from flask_login import login_required
from flask import request

from app import socketio, db
from app.models import Message, Room, User


def token_requered(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        resp = User.decode_auth_token(request.args.get('token', '12345'))
        if not isinstance(resp, int):
            print('Clent disconnected')
            send('disconnected')
            disconnect()
        else:
            print('accepted')
            return f(*args, **kwargs)
    return wrapper


@socketio.on('connect')
def on_connect():
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
        response[room.name]['count'] = u.viewed[room.name]
        response[room.name]['users'] = [u.username for u in room.users if u.username != username] 

        join_room(room.name)
    emit('get_messages', response)
    print(f'sent {len(response)} rooms')
        

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


@socketio.on('send_message')
def on_message(data):
    print('DEBUG', request.json)
    room = data.pop('room')
    data['room_id'] = Room.query.filter_by(name=room).first().id
    u = User.query.filter_by(username=data['username']).first()

    r = Room.query.filter_by(name=room).first()

    for user in r.users:
        viewed = user.viewed.copy()
        viewed[room] += 1
        user.viewed = viewed

    m = Message(**data)
    v = u.viewed
    v[room] = 0
    u.viewed = v
    db.session.add(m)
    db.session.commit()
    emit('new_message', m.serialize, room=room)
    print(f'new message from {m.username} to {room}')


@socketio.on('view')
def on_view(data):
    username = data['username']
    room = data['room']
    u = User.query.filter_by(username=username).first()
    u.view_room(room)
    r = Room.query.filter_by(name=room).first()
    messages = r.messages.all()
    print(f'sent {len(messages)} messages')
    emit('room_messages', [ms.serialize for ms in messages])
р

@socketio.on('update_last_seen')
def on_update_last_seen(data):
    username = data['username']
    u = User.query.filter_by(username=username).first()
    print(u.last_seen)
    u.last_seen = datetime.datetime.utcnow()
    db.session.commit()

    u = User.query.filter_by(username=username).first()
    print(u.last_seen)

