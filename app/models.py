# -*- coding=utf-8 -*-
from . import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash  # 引入密码加密 验证方法
from flask_login import LoginManager
from datetime import datetime
from flask_login import UserMixin
import hashlib
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from sqlalchemy import Float


class User(UserMixin,db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    password_hash = db.Column(db.String(128))
    articles = db.relationship('Article', backref='user')

    @property
    def password(self):
        raise AttributeError(u'密码属性不正确')

    def is_active(self):
        return True

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
        # 增加password会通过generate_password_hash方法来加密储存

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
        # 在登入时,我们需要验证明文密码是否和加密密码所吻合



class Record(db.Model):
    __tablename__ = 'record'
    id = db.Column(db.Integer, primary_key=True)
    create_time = db.Column(db.DATETIME)
    comment = db.Column(db.Text)
    comment_html = db.Column(db.Text)
    verify = db.Column(db.Boolean, default=False)

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p','img']
        attrs = {
            'img': ['src', 'alt'],
            'a': ['href','rel']
        }
        target.comment_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True, attributes=attrs))

db.event.listen(Record.comment, 'set', Record.on_changed_body)


from markdown import markdown
import bleach
class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), unique=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    create_time = db.Column(db.DATETIME, default=datetime.utcnow())
    category_id = db.Column(db.Integer, db.ForeignKey('categorys.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    comments = db.relationship('Comment', backref='articles', lazy='dynamic')

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p','img']
        attrs = {
            'img': ['src', 'alt']
        }
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True, attributes=attrs))

db.event.listen(Article.body, 'set', Article.on_changed_body)

class Category(db.Model):
    __tablename__ = 'categorys'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    articles = db.relationship('Article', backref='category',lazy='dynamic')

class C5game(db.Model):
    __tablename__ = 'c5game'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    address = db.Column(db.String(64), unique=True)
    price = db.Column(db.Float)
    min = db.Column(db.Float)
    verify = db.Column(db.Boolean, default=True)

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    create_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    name = db.Column(db.String(64))
    email = db.Column(db.String(64))
    post_id = db.Column(db.Integer, db.ForeignKey('articles.id'))

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code', 'em', 'i',
        'strong']
        target.body_html = bleach.linkify(bleach.clean(
        markdown(value, output_format='html'),
        tags=allowed_tags, strip=True))

db.event.listen(Comment.body, 'set', Comment.on_changed_body)




@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))