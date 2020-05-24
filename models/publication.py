from models.db import db
from models.feedback import Feedback
from datetime import datetime


class Publication(db.Model):
    __tablename__ = 'publication'

    id = db.Column('id', db.Integer, primary_key=True)
    doi = db.Column('doi', db.String(100))
    preInvocId = db.Column('preinvocid', db.String(200), unique=True)
    postInvocId = db.Column('postinvocid', db.String(200), unique=True)
    databaseId = db.Column('databaseid', db.Integer, nullable=False)
    displayName = db.Column('displayname', db.String)
    status = db.Column('status', db.String(120), default='started')
    okAuthor = db.Column('okauthor', db.DateTime)
    published = db.Column('published', db.DateTime)
    exported = db.Column('exported', db.DateTime)
    feedbacks = db.relationship('Feedback', backref='publication', lazy=True)

    def __repr__(self):
        return '<Publication invocId {}, databaseId {} and status {}'.format(
            self.preInvocId,
            self.databaseId,
            self.status)

    def __init__(self,
                 doi,
                 invocId,
                 databaseId,
                 displayName='',
                 status='started'):
        self.databaseId = databaseId
        self.doi = doi
        self.preInvocId = invocId
        self.displayName = displayName
        self.status = status

    def format(self):
        self.actualize_status()
        response = {
            'id': self.id,
            'invocationId': self.preInvocId,
            'doi': self.doi,
            'displayName': self.displayName,
            'status': self.status
            }
        if self.okAuthor is not None:
            response["okAuthor"] = self.okAuthor.strftime('%d.%m.%Y')
        if self.published is not None:
            response["published"] = self.published.strftime('%d.%m.%Y')
        if self.exported is not None:
            response["exported"] = self.exported.strftime('%d.%m.%Y')
        return response

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def publish(self):
        self.published = datetime.now()
        db.session.commit()

    def export(self):
        self.exported = datetime.now()
        db.session.commit()

    def registerOk(self):
        self.okAuthor = datetime.now()
        db.session.commit()

    def actualize_status(self):
        if self.exported is not None:
            self.status = 'exported'
        elif self.published is not None:
            self.status = 'published'
        else:
            done = True
            for f in self.feedbacks:
                done = done and f.done
            if done:
                self.status = 'finished'
            else:
                self.status = 'feedbacks to do'
