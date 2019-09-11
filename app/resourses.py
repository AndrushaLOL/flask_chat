from flask_restful import Resource
from flask import request
from app import db, api
from app.models import Message, Room, User

def succes(**kwargs):
    res = {'status': 'success', **kwargs}
    return res

def error(**kwargs):
    res = {'status': 'error', **kwargs}
    return res

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
        return succes()

    def delete(self, id):
        m = Message.query.get(id)
        db.session.delete(m)
        db.session.commit()

        return succes()


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

        return succes(**m.serialize)


class RoomApi(Resource):
    def post(self):
        data = request.get_json()
        r = Room(name=data['name'])
        users = data['users']
        for username in users:
            u = User.query.filter_by(username=username).first()
            v = u.viewed.copy()
            v[r.name] = 0
            u.viewed = v
            print(u.viewed)
            u.rooms.append(r)
        db.session.add(r)
        db.session.commit()
        return succes(id=r.id, name=r.name)

    def delete(self):
        data = request.get_json()
        r = Room.query.filter_by(name=data['name']).first()
        db.session.delete(r)
        db.session.commit()

        return succes()


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
        if 'photo_url' not in data:
            u.photo_url = u.avatar(128)
        u.set_password(password)
        db.session.add(u)
        db.session.commit()

        return succes(token=u.encode_auth_token().decode())


class UserApi(Resource):
    def get(self, username):
        u = User.query.filter_by(username=username).first()
        try:
            return succes(**u.serialize, friends=[f.serialize() for f in u.friends])
        except Exception as e:
            return error(message='Something went wrong')

    
    def delete(self, username):
        u = User.query.filter_by(username=username).first()
        try:
            db.session.delete(u)
            db.session.commit()
            return succes()
        except:
            return error(message='Something went wrong')


class AddUserApi(Resource):
    def get(self, username, roomname):
        u = User.query.filter_by(username=username).first()
        r = Room.query.filter_by(name=roomname).first()
        u.rooms.append(r)
        db.session.commit()

class AddFriend(Resource):
    def get(self, username, friend):
        u = User.query.filter_by(username=username).first()
        f = User.query.filter_by(username=username).first()

        u.add_friend(f)

        db.session.commit()
        return succes()
    
    def delete(self, username, friend):
        u = User.query.filter_by(username=username).first()
        f = User.query.filter_by(username=username).first()

        u.delete_friend(f)

        db.session.commit()
        return succes()
        


api.add_resource(UserListApi, '/api/user', endpoint='users')
api.add_resource(AddUserApi, '/api/user/<string:username>/<string:roomname>/', endpoint='add')
api.add_resource(UserApi, '/api/user/<string:username>', endpoint='user')
api.add_resource(RoomApi, '/api/room', endpoint='rooms')
api.add_resource(MessageListAPI, '/api/message', endpoint='messages')
api.add_resource(MessageAPI, '/api/message/<int:id>', endpoint='message')