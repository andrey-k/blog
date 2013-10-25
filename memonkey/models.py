from datetime import datetime
from sqlalchemy_utils import PasswordType
from wtforms_alchemy import ModelForm
from wtforms.fields import TextField

import flask.ext.whooshalchemy as whooshalchemy

from memonkey import app
from memonkey import db

class Users(db.Model):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(Unicode(100), nullable=False)
    password = db.Column(
        PasswordType(
            schemes=['pbkdf2_sha512']
        ),
        nullable=False
    )

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def __init__(self, name, password):
        self.name = name
        self.password = password



class UserForm(ModelForm):
    class Meta:
        model = Users

    required_validator = Users.password

association_table = db.Table('association',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'))
)

class Post(db.Model):
    __searchable__ = ['title', 'body']

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    body = db.Column(db.Text, nullable=False)
    pub_date = db.Column(db.DateTime)

    categories = db.relationship('Category', secondary=association_table,
                            backref=db.backref('posts', lazy='dynamic'))

    def __init__(self, title, body, pub_date=None):
        self.title = title
        self.body = body
        if pub_date is None:
            pub_date = datetime.utcnow()
        self.pub_date = pub_date

    def __repr__(self):
        return '<Post %r>' % self.title

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Category %r>' % self.name

class PostForm(ModelForm):
    class Meta:
        model = Post
        exclude = ['pub_date', 'user_id']

    tags = TextField()

whooshalchemy.whoosh_index(app, Post)

class SearchForm(ModelForm):
    search = TextField(validators=[DataRequired()])