from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

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

@db.event.listens_for(Book, 'before_update')
def insert_audit_before_update(mapper, connection, target):
    db.session.add(Audit(book_id=target.id, action='update'))
    print(f'Audit record created relating BOOK "{target.id}" UPDATE')
