import click
from flask.cli import with_appcontext
from .models import db, Book, AuditLog
from sqlalchemy.orm import sessionmaker
from flask import jsonify, current_app
import sqlite3
import sqlalchemy.exc
import time


# @click.command('test-sessions')
# @with_appcontext
# def test_sessions():
#     """Initialize the database and populate it with sample data."""

#     # Create a session factory bound to your engine
#     Session = sessionmaker(bind=db.engine)

#     try:

#          # First operation: Add a new book using the default session
#         _title = "Sample Book 3"
#         _author = "Author Goofy"
#         book3 = Book(title=_title, author=_author)
#         db.session.add(book3)
#         db.session.commit()
#         click.echo(f'Book {_title} by {_author} added.')


#          # Second operation: Modify an existing book using the default session
#         first_book_id = 1
#         book = Book.query.get(first_book_id)
#         new_title = 'Cippalus'
#         if not book:
#             raise ValueError(f'Book with ID {first_book_id} not found.')
#         book.title = new_title
#         db.session.commit()
#         click.echo(f'Update Book with ID {first_book_id} with new title: {new_title}')
#     except Exception as e:
#         print(e)
#         db.session.rollback()

#     try:
#         new_session = Session()

#         unexisting_book_id = 999
#         new_title = "Alfa srl"

#         book = new_session.query(Book).get(unexisting_book_id)

#         if not book:
#             raise ValueError(f'Book with ID {unexisting_book_id} not found.')

#         book.title = new_title
#         new_session.commit()
#         click.echo(f'Book with ID {unexisting_book_id} updated to {new_title}.')
#     except Exception as e:
#         click.echo(f'Error updating book: {e}')
#         new_session.rollback()
#     finally:
#         new_session.close()


# @click.command('test-sessions-2')
# @with_appcontext
# def test_sessions_2():
#     """Initialize the database and populate it with sample data."""

#     try:

#          # First operation: Add a new book using the default session
#         _title = "Sample Book 3"
#         _author = "Author Goofy"
#         book3 = Book(title=_title, author=_author)
#         db.session.add(book3)
#         db.session.commit()
#         click.echo(f'Book {_title} by {_author} added.')


#          # Second operation: Modify an unexisting book using the default session
#         _book_id = 999
#         book = Book.query.get(_book_id)
#         new_title = 'Cippalus'
#         if not book:
#             raise ValueError(f'Book with ID {_book_id} not found.')
#         book.title = new_title
#         db.session.commit()
#         click.echo(f'Update Book with ID {_book_id} with new title: {new_title}')

#         # First operation: Add a new book using the default session
#         _title = "Sample Book 4"
#         _author = "Author Max Goof"
#         book4 = Book(title=_title, author=_author)
#         db.session.add(book4)
#         db.session.commit()
#         click.echo(f'Book {_title} by {_author} added.')
#     except Exception as e:
#         print(e)
#         db.session.rollback()


# @click.command('test-sessions-3')
# @with_appcontext
# def test_sessions_3():

#     books = [
#         Book(title='A', author='Gino'),
#         Book(title='B', author='Gina'),
#         Book(title='C', author='Pina')
#     ]

#     try:
#         for b in books:
#             db.session.add(b)
#             db.session.commit()
#     except Exception as e:
#         print(e)
#         db.session.rollback()



class DatabaseCommands:

    @staticmethod
    def clear_db_logic():
        try:
            db.drop_all()
            db.create_all()
            click.echo('All tables have been cleared.')
        except Exception as e:
            click.echo(f'Error clearing tables: {e}')

    @staticmethod
    def init_db_logic():
        db.create_all()

        try:
            if not Book.query.filter_by(title="Sample Book 1").first():
                book1 = Book(title="Sample Book 1", author="Author Donald")
                db.session.add(book1)

            if not Book.query.filter_by(title="Sample Book 2").first():
                book2 = Book(title="Sample Book 2", author="Author Duck")
                db.session.add(book2)

            db.session.commit()

            click.echo("Database initialized and sample books added or updated.")
        except Exception as e:
            print(e)
            db.session.rollback()

    @staticmethod
    def add_sample_books():

        books = [
            Book(title='A', author='Gino'),
            Book(title='B', author='Gina'),
            Book(title='C', author='Pina')
        ]

        try:
            for b in books:
                db.session.add(b)
                db.session.commit()
                click.echo(f"Added New Book: {b.to_dict()}")
        except Exception as e:
            print(e)
            db.session.rollback()

    @staticmethod
    def update_books_with_IntegrityError():
        
            book_map_to_update = {
                'A': 'Cippalippa',
                'B': None,
                'C': 'Cippalippa'
            }
            for b_title, b_author in book_map_to_update.items():
                try:
                    book = Book.query.filter_by(title=b_title).first()
                    if book:
                        book.author = b_author
                        db.session.commit()
                except (sqlalchemy.exc.IntegrityError, sqlite3.IntegrityError) as sqle:
                    print(sqle)
                    db.session.rollback()
                except Exception as e:
                    print(e)

    @staticmethod
    def update_books_with_exception():
        
            book_map_to_update = {
                'A': 'Cippalippa',
                'B': None,
                'C': 'Cippalippa'
            }
            for b_title, b_author in book_map_to_update.items():
                try:
                    book = Book.query.filter_by(title=b_title).first()
                    if book:
                        book.author = b_author
                        db.session.commit()
                except Exception as e:
                    print(e)
                    db.session.rollback()

    @staticmethod
    def list_all():
        """Print all books and audits."""

        books = Book.query.all()
        click.echo('Books:')
        for book in books:
            click.echo(book.to_dict())

        click.echo('+++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        audits = AuditLog.query.all()
        click.echo('Audits:')
        for audit in audits:
            click.echo(audit.to_dict())

    @staticmethod
    @click.command('init-db')
    @with_appcontext
    def init_db_command():
        """Initialize the database and populate it with sample data."""
        DatabaseCommands.init_db_logic()

    @staticmethod
    @click.command('clear-db')
    @with_appcontext
    def clear_db_command():
        """Clear all tables in the database."""
        DatabaseCommands.clear_db_logic()

    @staticmethod
    @click.command('add-sample-books')
    @with_appcontext
    def add_sample_books_command():
        """Add sample books in the database."""
        DatabaseCommands.add_sample_books()

    @staticmethod
    @click.command('reset-db')
    @with_appcontext
    def reset_db_command():
        """Clear all tables, then initialize the database and populate it with sample data."""
        DatabaseCommands.clear_db_logic()
        DatabaseCommands.init_db_logic()
        DatabaseCommands.add_sample_books()

    @staticmethod
    @click.command('test-1')
    @with_appcontext
    def update_books_with_IntegrityError_command():
        DatabaseCommands.update_books_with_IntegrityError()

    @staticmethod
    @click.command('test-2')
    @with_appcontext
    def update_books_with_exception_command():
        DatabaseCommands.update_books_with_exception()

    @staticmethod
    @click.command('list-all')
    @with_appcontext
    def list_all_command():
        DatabaseCommands.list_all()

    @staticmethod
    @click.command('create-book')
    @click.argument('title')
    @click.argument('author')
    @with_appcontext
    def create_book(title, author):
        try:
            book = Book(title=title, author=author)
            db.session.add(book)
            db.session.commit()
            click.echo(f'Book {title} by {author} added.')
        except Exception as e:
            click.echo(f'Error creating book: {e}')
            db.session.rollback()

    @staticmethod
    @click.command('update-book')
    @click.argument('id', type=int)
    @click.argument('new_title')
    @with_appcontext
    def update_book(id, new_title):
        try:
            book = Book.query.get(id)

            if not book:
                raise ValueError(f'Book with ID {id} not found.')

            book.title = new_title
            db.session.commit()
            click.echo(f'Book {title} by {author} added.')
                
        except Exception as e:
            click.echo(f'Error updating book: {e}')
            db.session.rollback()

    @classmethod
    def register_commands(cls, app):
        app.cli.add_command(cls.init_db_command)
        app.cli.add_command(cls.clear_db_command)
        app.cli.add_command(cls.reset_db_command)
        app.cli.add_command(cls.add_sample_books_command)
        app.cli.add_command(cls.update_books_with_IntegrityError_command)
        app.cli.add_command(cls.update_books_with_exception_command)
        app.cli.add_command(cls.list_all_command)
        app.cli.add_command(cls.update_book)
        app.cli.add_command(cls.create_book)
        # ... (registra altri comandi)

def init_app(app):
    DatabaseCommands.register_commands(app)