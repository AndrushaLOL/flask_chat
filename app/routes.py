from app import app, db
from flask_restful import Resource, marshal
from flask import request, jsonify, g
from app.models import User
from app.send_sms import send_sms, generate_code


@app.route('/')
@app.route('/index')
def index():
    return 'Hello!'


@app.route('/api/v1.0/register', methods=['POST'])
def register():
    phone = request.json.get('phone')
    u = User.query.filter_by(phone=phone).first()
    if u:
        return {'status': 'error', 'message': f'User with phone {phone} already exists'}
    # code = generate_code()
    # send_sms(phone, code)

    user = User(phone=phone, active=True, code=code)
    db.session.add(user)
    db.session.commit()

    return jsonify({'status': 'ok', 'phone': phone})


@app.route('/api/v1.0/verify', methods=['POST'])
def verify():
    phone = request.json.get('phone')
    code = request.json.get('code')
    user = User.query.filter_by(phone=phone).first()
    if user.code == code:
        user.active = True
        db.session.commit()
        return {'message': 'success'}
    else:
        return {'message': 'Wrong code'}