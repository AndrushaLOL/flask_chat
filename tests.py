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
        u = User(username='test', email='test@mail.ru')
        db.session.add(u)
        db.session.commit()
        self.assertEqual(u.username, 'test')
        self.assertEqual(u.viewed, {})
        self.assertEqual(u.messages.all(), [])
        self.assertEqual(u.rooms, [])
        self.assertEqual(u.friends.all(), [])

    def test_add_room(self):
        u = User(username='test_user', email='test@mail.ru')
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
        u1 = User(username='test_user1', email='test@mail.ru')
        u2 = User(username='test_user2', email='test2@mail.ru')

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

    def test_friends(self):
        u1 = User(username='test_user1', email='test@mail.ru')
        u2 = User(username='test_user2', email='test2@mail.ru')

        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

        u1.add_friend(u1)
        db.session.commit()
        self.assertEqual(u1.friends.all(), [])
        u1.add_friend(u2)
        db.session.commit()
        self.assertEqual(u1.friends.all(), [u2])
        self.assertEqual(u2.friends.all(), [u1])


if __name__ == '__main__':
    unittest.main(verbosity=2)