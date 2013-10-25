#!flask/bin/python
import os
import unittest

from config import basedir
from memonkey import app, db
from memonkey.models import Users

class TestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def login(self, username, password):
        return self.app.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    def test_login_logout(self):
        rv = self.login('qwe', 'qwerty')
        assert 'You were logged in' in rv.data
        rv = self.logout()
        assert 'You were logged out' in rv.data
        rv = self.login('qwerrr', 'qwerty')
        assert 'Invalid username' in rv.data
        rv = self.login('qwe', 'asasdsd')
        assert 'Invalid password' in rv.data

if __name__ == '__main__':
    unittest.main()