from flask import redirect, request, jsonify
from flask_login import current_user, login_user, logout_user
from app.models import User
from app import app


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    u = User.query.filter_by(username=data['username']).first()
    if u is None:
        return jsonify({'status': 'failed', 'message': 'User not found.'})
    if u.check_password(data['password']):
        token = u.encode_auth_token()
        return jsonify({"token": token.decode()})