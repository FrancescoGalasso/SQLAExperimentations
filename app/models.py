import datetime
import json

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.orm.attributes import get_history


db = SQLAlchemy()
audits_to_register = []


class BaseModel(db.Model):
    __abstract__ = True  # BaseModel should not be used as a standalone table.
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    def to_dict(self):
        raise NotImplementedError("Subclasses must implement this method.")


class Author(BaseModel):
    name = db.Column(db.String(80), nullable=False)

    def to_dict(self):
        """Return the model as a dictionary."""
        return {
            'id': self.id,
            'name': self.name
        }


class Book(BaseModel):
    title = db.Column(db.String(80), nullable=False)
    genre = db.Column(db.String(50))
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'), nullable=False)
    author = db.relationship('Author')

    def to_dict(self):
        """Return the model as a dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'genre': self.genre,
            'author_id': self.author_id,
            'author_name': self.author.name if self.author else None
        }


class AuditLog(BaseModel):
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    action = db.Column(db.String(10), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    history = db.Column(db.Text)

    def to_dict(self):
        """Return the model as a dictionary."""
        return {
            'id': self.id,
            'book_id': self.book_id,
            'action': self.action,
            'timestamp': datetime.datetime.strftime(self.timestamp, '%Y-%m-%d %H:%M:%S') if self.timestamp else None,
            'history': self.history
        }

def configure_event_listeners(app):

    @event.listens_for(db.session, 'after_flush')
    def db_after_flush(session, flush_context):
        for instance in session.new:
            if isinstance(instance, AuditLog):
                continue
            print(f'instance -> {instance}')
        for instance in session.dirty:
            if isinstance(instance, AuditLog):
                continue
            if isinstance(instance, Book):
                history = {}
                if get_history(instance, 'title').has_changes():
                    changes = get_history(instance, 'title')
                    old_value = changes.deleted[0] if changes.deleted else None
                    new_value = changes.added[0] if changes.added else None
                    history['Book title'] = {'old': old_value, 'new': new_value}
                if get_history(instance, 'author_id').has_changes():
                    changes = get_history(instance, 'author_id')
                    old_author = Author.query.get(changes.deleted[0]) if changes.deleted else None
                    new_author = Author.query.get(changes.added[0]) if changes.added else None

                    history[f'Book author'] = {
                        'old': old_author.name if old_author else None,
                        'new': new_author.name if new_author else None
                    }
                if len(history):
                    print(f'history: {history}')
                    al = AuditLog(
                        book_id=instance.id,
                        action='UPDATE',
                        history=json.dumps(history)
                    )
                    print(f'history AFTER FLUSH-> {history}')
                    audits_to_register.append(al)
                    print(f'AuditLog: {al.to_dict()}')

        for instance in session.new:
            if isinstance(instance, AuditLog):
                pass

            if isinstance(instance, Book):
                print('Book added to DB!')

    @event.listens_for(db.session, 'after_commit')
    def db_after_transaction_end(session):
        """
        Use the core API to insert Audits into the Audit table
        """
        if audits_to_register:
            print(audits_to_register)

            audit_table = AuditLog.__table__
            engine = db.get_engine(db.session.bind)
            connection = engine.connect()
            for a in audits_to_register:
                try:
                    stmt = audit_table.insert().values(**a.to_dict())
                    connection.execute(stmt)
                except Exception as e:
                    print(e)
                    connection.rollback()

            audits_to_register.clear()
