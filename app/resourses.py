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


class MessageListAPI(Resource):
    def get(self):
        return [m.serialize for m in Message.query.all()]
    
    def post(self):
        data = request.get_json()
        print(data)
        rid = Room.query.filter_by(name=data.pop('room')).first().id
        if rid is None:
            return 'No room'
        data['room_id'] = rid
        m = Message(**data)
        db.session.add(m)
        db.session.commit()

        return m.serialize


class RoomApi(Resource):
    def post(self):
        data = request.get_json()
        r = Room(name=data['name'])
        db.session.add(r)
        db.session.commit()
        return {'id': r.id, 'name': r.name}


class UserApi(Resource):
    def post(self):
        data = request.get_json()
        data['active'] = True
        u = User(**data)
        db.session.add(u)
        db.session.commit()

        return {'id': u.id, 'username': u.username}

class AddUserApi(Resource):
    def get(self, username, roomname):
        u = User.query.filter_by(username=username).first()
        r = Room.query.filter_by(name=roomname).first()
        u.rooms.append(r)
        db.session.commit()

api.add_resource(AddUserApi, '/api/user/<string:username>/<string:roomname>/', endpoint='add')
api.add_resource(UserApi, '/api/user', endpoint='users')
api.add_resource(RoomApi, '/api/room', endpoint='rooms')
api.add_resource(MessageListAPI, '/api/message', endpoint='messages')
api.add_resource(MessageAPI, '/api/message/<int:id>', endpoint='message')