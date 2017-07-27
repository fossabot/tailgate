import datetime
import author_list
import logging

log = logging.getLogger("models")

def build_models(db):
    class User(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String, nullable=False)
        token = db.Column(db.String, nullable=False)
        token_secret = db.Column(db.String, nullable=False)
    
    class Follows(db.Model):
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
        follows = db.Column(db.Integer, db.ForeignKey('author.id'), primary_key=True)

    class Author(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String, nullable=False)
        last_updated = db.Column(db.DateTime, nullable=True)
        books = db.relationship('Book', backref='author', lazy='dynamic')

        def update_books(self, session):
            if self.last_updated is None or self.last_updated + datetime.timedelta(days=1) < datetime.datetime.now():
                log.info("Updating %s" % self.name)
                books = author_list.get_books(session, self)
                for book in self.books:
                    db.session.delete(book)
                for title, values in books.items():
                    db.session.add(Book(id=values["id"], title=title, published=values["when"], author=self))
                self.last_updated = datetime.datetime.now()
                db.session.commit()

    class Book(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String, nullable=False)
        published = db.Column(db.DateTime, nullable=False)
        author_id = db.Column(db.Integer, db.ForeignKey('author.id'), nullable=False)

    return (User, Follows, Author, Book)