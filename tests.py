import unittest

from app import app, db
from app.models import User, Room, Message

class UserTestCase(unittest.TestCase):

    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_create_user(self):
        u = User(username='test', phone='895123')
        db.session.add(u)
        db.session.commit()
        self.assertEqual(u.username, 'test')
        self.assertEqual(u.viewed, {})
        self.assertEqual(u.messages.all(), [])
        self.assertEqual(u.rooms, [])

    def test_add_room(self):
        u = User(username='test_user', phone='123')
        r = Room(name='test_room')
        db.session.add(u)
        db.session.add(r)
        db.session.commit()
        self.assertEqual(r.users, [])
        self.assertEqual(u.rooms, [])

        u.rooms.append(r)
        db.session.commit()
        self.assertEqual(r.users, [u])
        self.assertEqual(u.rooms, [r])

    def test_new_message(self):
        u1 = User(username='test_user1', phone='123')
        u2 = User(username='test_user2', phone='1234')

        r = Room(name='test_room')

        m1 = Message(username=u1.username, text='test_message1', room=r)
        m2 = Message(username=u2.username, text='test_message2', room=r)

        db.session.add(u1)
        db.session.add(u2)
        db.session.add(r)
        db.session.add(m1)
        db.session.add(m2)

        db.session.commit()

        self.assertEqual(u1.messages.all(), [m1])
        self.assertEqual(u2.messages.all(), [m2])
        self.assertEqual(r.messages.all(), [m1, m2])
        self.assertEqual(m1.user, u1)
        self.assertEqual(m2.user, u2)
        self.assertEqual(m1.room, r)
        self.assertEqual(m2.room, r)


if __name__ == '__main__':
    unittest.main(verbosity=2)