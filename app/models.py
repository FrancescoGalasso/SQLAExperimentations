from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
audits_to_register = []

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(80), nullable=False)
    author = db.Column(db.String(80), nullable=False)

class Audit(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    action = db.Column(db.String(10), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Event listeners #

# @db.event.listens_for(Book, 'before_insert')
# def insert_audit_before_insert(mapper, connection, target):
#     db.session.add(Audit(book_id=target.id, action='insert'))

# @db.event.listens_for(Book, 'before_update')
# def insert_audit_before_update(mapper, connection, target):
#   """
#   raising SAWarning:
#   Usage of the 'Session.add()' operation is not currently supported within
#   the execution stage of the flush process. Results may not be consistent.
#   Consider using alternative event listeners or connection-level operations instead.
#   """

#   db.session.add(Audit(book_id=target.id, action='update'))
#   print(f'Audit record created relating BOOK "{target.id}" UPDATE')

# @db.event.listens_for(Book, 'before_update')
# def insert_audit_before_update(mapper, connection, target):
#   """
#     Use the core API to insert into the Audit table
#     """
#     audit_table = Audit.__table__
#     stmt = audit_table.insert().values(book_id=target.id, action='update')
#     connection.execute(stmt)
#     print(f'Audit record created relating BOOK "{target.id}" UPDATE')

def configure_listeners(app):
    from sqlalchemy import event

    @db.event.listens_for(Book, 'before_update')
    def create_audit_before_update(mapper, connection, target):
        """
        Use the core API to insert into the Audit table
        """

        audit = Audit(book_id=target.id, action='update')
        audits_to_register.append(audit)


    @db.event.listens_for(db.session, 'after_commit')
    def insert_audit_after_commit(session):
        """
        Use the core API to insert into the Audit table
        """

        # audit = Audit(book_id=target.id, action='update')
        # audits_to_register.append(audit)
        # print(audits_to_register)
        print(audits_to_register)

    @db.event.listens_for(db.session, 'after_rollback')
    def log_after_rollback(session):
        """
        Log or perform actions after a rollback event.
        """
        print("A rollback has occurred. Any transactional changes since the last commit have been reverted.")
