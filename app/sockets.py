from app import socketio
from flask_socketio import join_room, leave_room, send, emit


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
    semd(f'{username} disconnected from the room.', room=room)


@socketio.on('message')
def on_message(data):
    print(data)


@socketio.on('my event')
def on_my_event(data):
    print(data)

