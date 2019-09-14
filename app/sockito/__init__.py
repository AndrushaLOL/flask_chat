from app import socketio
from pydantic import ValidationError

class BaseHandler():
    _event = ''
    _model = None
    _db_model = None
    _notify_all = False

    @app.socketio(f'{self._event}_create')
    def create(self, data):
        room, data = self._extract_room(data)
        validated, m = self._validate(data)
        if validated:
            db.session.add(m)
            db.session.commit()
            if room:
                emit(f'back_{self._event}_create', m.serilize, room=room)
            return
        send('Validation Error')
            

    @app.socketio(f'{self._event}_read')
    def read(self, data):
        m = self._db_model.query.get(data['id'])
        send(m)

    def update(self, data):
        room, data = self._extract_room(data)
        validated, m = self._validate(data)
        if validated:
            for k, v in data.items():
                setattr(m, k, v)
            db.session.commit()
            m = self._db_model.query.get(data['int'])
            if room:
                emit(f'back_{self._event}_update', m.serilize, room=room)
            return
        send('Validation Error')

    def delete(self, data):
        room, data = self._extract_room(data)
        validated, m = self._validate(data)
        if validated:
            db.session.delete(m)
            db.session.commit()
            if room:
                emit(f'back_{self._event}_update', m.id, room=room)
            return 
        send('Validation Error')

    def _validate(self, data):
        try:                
            self._model(**data)
            return True, self._db_model(**data)
        except ValidationError as e:
            print(e.json())
            return False, None

    def _extract_room(self, data):
        if 'room' in data:
            return data.pop('room'), data