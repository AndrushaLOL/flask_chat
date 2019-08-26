from flask_restful import Resource
from flask import request
from app import db, api
from app.models import Message, Room, User


class MessageAPI(Resource):
    def get(self, id):
        m = Message.query.get(id)
        return m.serialize

    def put(self, id):
        m = Message.query.get(id)
        data = request.get_json()
        print(data)
        for k, v in data.items():
            setattr(m, k, v)
        db.session.commit()
        print(m.text)
        return {}

    def delete(self, id):
        m = Message.query.get(id)
        db.session.delete(m)
        db.session.commit()

        return {'status': 'ok'}


class MessageListAPI(Resource):
    def get(self):
        return [m.serialize for m in Message.query.all()]
    
    def post(self):
        data = request.get_json()
        print(data)
        rid = Room.query.filter_by(name=data.pop('room')).first().id
        if rid is None:
            return {'status': 'failed', 'message': 'Room not found'}
        data['room_id'] = rid
        m = Message(**data)
        db.session.add(m)
        db.session.commit()

        return {'status': 'ok', **m.serialize}


class RoomApi(Resource):
    def post(self):
        data = request.get_json()
        r = Room(name=data['name'])
        users = data['users']
        for username in users:
            u = User.query.filter_by(username=username).first()
            u.rooms.append(r)
        db.session.add(r)
        db.session.commit()
        return {'id': r.id, 'name': r.name, 'status': 'ok'}

    def delete(self):
        data = request.get_json()
        r = Room.query.filter_by(name=data['name']).first()
        db.session.delete(r)
        db.session.commit()

        return {'status': 'ok'}


class UserListApi(Resource):
    def get(self):
        us = User.query.all()
        return [u.username for u in us]

    def post(self):
        data = request.get_json()
        data['active'] = True
        data['viewed'] = dict()
        password = data.pop('password')
        u = User(**data)
        u.set_password(password)
        db.session.add(u)
        db.session.commit()

        return {'status': 'ok', 'token': u.encode_auth_token().decode()}


class UserApi(Resource):
    def get(self, username):
        u = User.query.filter_by(username=username).first()
        if u is None:
            return 'User not found'
        return {'username': username}
    
    def delete(self, username):
        u = User.query.filter_by(username=username).first()
        if u in None:
            return {'status': 'Failed', 'message': 'User Not Found'}
        db.session.remove(u)
        db.session.commit()
        return {'status': 'ok'}


class AddUserApi(Resource):
    def get(self, username, roomname):
        u = User.query.filter_by(username=username).first()
        r = Room.query.filter_by(name=roomname).first()
        u.rooms.append(r)
        db.session.commit()


api.add_resource(UserListApi, '/api/user', endpoint='users')
api.add_resource(AddUserApi, '/api/user/<string:username>/<string:roomname>/', endpoint='add')
api.add_resource(UserApi, '/api/user/<string:username>', endpoint='user')
api.add_resource(RoomApi, '/api/room', endpoint='rooms')
api.add_resource(MessageListAPI, '/api/message', endpoint='messages')
api.add_resource(MessageAPI, '/api/message/<int:id>', endpoint='message')