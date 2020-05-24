# Imports #
from models.db import db


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    identifier = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(120))
    email = db.Column(db.String(120))
    roles = db.Column(db.String(120))
    feedbacks = db.relationship('Feedback', backref='author', lazy=True)

    def __repr__(self):
        return '<Person id {}, name {} email {}'.format(
            self.id,
            self.name,
            self.email)

    def __init__(self, name, email=''):
        self.name = name
        self.email = email

    def format(self):
        return {
            'name': self.name,
            'roles': self.get_roles()
        }

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def get_roles(self):
        return self.roles.split(',')

    def add_role(self, role):
        if self.roles is None:
            roles = []
        else:
            roles = self.roles.split(',')
        roles.append(role)
        self.roles = ','.join(roles)
        self.update()
