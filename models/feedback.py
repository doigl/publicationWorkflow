from models.db import db
# from models.role import Role


class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    publication_id = db.Column(db.Integer, db.ForeignKey('publication.id'))
    feedback = db.Column(db.Text, nullable=False)
    done = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<Feedback to publication {} from author {}: {}'.format(
            self.publication_id,
            self.author,
            self.feedback)

    def __init__(self, publication_id, feedback, author_id=None):
        self.publication_id = publication_id
        self.feedback = feedback
        if author_id is not None:
            self.author_id = author_id

    def format(self):
        response = {
            'id': self.id,
            'publication': self.publication.format(),
            'text': self.feedback,
            'done': self.done
        }
        if self.author is not None:
            response["author"] = self.author.format()
        return response

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
