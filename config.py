import os
basedir = os.path.abspath(os.path.dirname(__file__))

CSRF_ENABLED = True
SECRET_KEY = 'some-very-secret-key'

SQLALCHEMY_DATABASE_URI = 'postgres://monkey:101bananas@127.0.0.1/monkey_db'

WHOOSH_BASE = os.path.join(basedir, 'search.db')

# pagination
POSTS_PER_PAGE = 10
MAX_SEARCH_RESULTS = 20