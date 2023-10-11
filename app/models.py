from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import datetime


db = SQLAlchemy()
audits_to_register = []

# class BasicModel(db.Model):
#     pass


class Book(db.Model):
    title = db.Column(db.String(80), nullable=False)
    author = db.Column(db.String(80), nullable=False)
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    def to_dict(self):
        """Return the model as a dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            # 'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }

class AuditLog(db.Model):
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    action = db.Column(db.String(10), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
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

# Event listeners #

def configure_listeners(app):
    from sqlalchemy import event
    import json
    from sqlalchemy.orm.attributes import get_history

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
                    history['title'] = get_history(instance, 'first_name')
                if get_history(instance, 'author').has_changes():
                    history['author'] = get_history(instance, 'author')
                if len(history):
                    al = AuditLog(
                        book_id=instance.id,
                        action='UPDATE',
                        history=json.dumps(history)
                    )
                    print(f'history -> {history}')
                    audits_to_register.append(al)
                    print(f'AuditLog: {al.to_dict()}')

        for instance in session.new:
            if isinstance(instance, AuditLog):
                pass

            if isinstance(instance, Book):
                print('Book added to DB!')

    # @event.listens_for(db.session, 'before_flush')
    # def db_before_flush(session, flush_context, instances):
    #     for instance in session.dirty:
    #         if isinstance(instance, AuditLog):
    #             continue
    #         if isinstance(instance, Book):
    #             history = {}
    #             if get_history(instance, 'title').has_changes():
    #                 history['title'] = get_history(instance, 'first_name')
    #             if get_history(instance, 'author').has_changes():
    #                 history['author'] = get_history(instance, 'author')
    #             if len(history):
    #                 al = AuditLog(
    #                     # request_id=str(g.request_id),
    #                     # model_name="user",
    #                     # original_id=instance.id,
    #                     # db_event_name="edit",
    #                     # history=json.dumps(history)
    #                     book_id=instance.id,
    #                     action='UPDATE',
    #                     history=json.dumps(history)
    #                 )
    #                 # session.add(al)
    #                 print(f'history -> {history}')
    #                 audits_to_register.append(al) 

    #     for instance in session.deleted:
    #         if isinstance(instance, AuditLog):
    #             continue
    #         if isinstance(instance, Book):
    #             pass
    #             # history = {
    #             #     'first_name': instance.first_name,
    #             #     'last_name': instance.last_name
    #             # }
    #             # if len(history):
    #             #     al = AuditLog(
    #             #         request_id=str(g.request_id),
    #             #         model_name="user",
    #             #         original_id=instance.id,
    #             #         db_event_name="delete",
    #             #         history=json.dumps(history)
    #             #     )
    #             #     session.add(al)

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
