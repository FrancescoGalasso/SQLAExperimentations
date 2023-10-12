import click
from flask.cli import with_appcontext
from .models import db, Book, Author, AuditLog
from sqlalchemy.orm import sessionmaker
from flask import jsonify, current_app
import sqlite3
import sqlalchemy.exc
import time
import traceback


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
            donald = Author(name="Author Donald")
            duck = Author(name="Author Duck")
            
            db.session.add_all([donald, duck])
            
            if not Book.query.filter_by(title="Sample Book 1").first():
                book1 = Book(title="Sample Book 1", author=donald)
                db.session.add(book1)

            if not Book.query.filter_by(title="Sample Book 2").first():
                book2 = Book(title="Sample Book 2", author=duck)
                db.session.add(book2)

            db.session.commit()
            click.echo("Database initialized and sample books added or updated.")
        except Exception as e:
            print(e)
            db.session.rollback()

    @staticmethod
    def add_sample_books():
        gino = Author(name='Gino')
        gina = Author(name='Gina')
        pina = Author(name='Pina')
        
        db.session.add_all([gino, gina, pina])
        db.session.commit()

        books = [
            Book(title='A', author=gino),
            Book(title='B', author=gina),
            Book(title='C', author=pina)
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
    def update_books_titles_with_IntegrityError():
        book_map_title_to_update = {
            'A': 'Cippalippa A',
            'B': None,
            'C': 'Cippalippa C'
        }
        for b_title, b_new_title in book_map_title_to_update.items():
            try:
                book = Book.query.filter_by(title=b_title).first()
                if book:
                    book.title = b_new_title
                    db.session.commit()
                    print(f"Updated Book: {book.to_dict()}")
            except (sqlalchemy.exc.IntegrityError, sqlite3.IntegrityError) as sqle:
                print(sqle)
                db.session.rollback()
            except Exception as e:
                db.session.rollback()
                print('Exception raised ..')
                print(traceback.format_exc())
                print(e)

    @staticmethod
    def update_books_author_with_IntegrityError():
        book_map_authors_to_update = {
            'Cippalippa C': 'Gina',
            'B': 'Scrooge'
        }

        for b_title, b_new_author in book_map_authors_to_update.items():
            try:
                book = Book.query.filter_by(title=b_title).first()
                if book:
                    new_author = Author.query.filter_by(name=b_new_author).first()
                    book.author_id = new_author.id
                    db.session.commit()
                    print(f"Updated Book: {book.to_dict()}")
            except (sqlalchemy.exc.IntegrityError, sqlite3.IntegrityError) as sqle:
                print(sqle)
                db.session.rollback()
            except Exception as e:
                db.session.rollback()
                print('Exception raised ..')
                print(traceback.format_exc())
                print(e)

    @staticmethod
    def raise_operational_db_error():
        """
        Monkey-patching the db.session commit to raise sqlite3.OperationalError

        https://en.wikipedia.org/wiki/Monkey_patch
        """

        book_map_title_to_update = {
            'Cippalippa A': 'Book Heroes',
        }

        # Monkey-patch db.session.commit
        original_commit = db.session.commit
        def failing_commit():
            raise sqlite3.OperationalError("Emulated driver error during commit")
        db.session.commit = failing_commit

        for b_title, b_new_title in book_map_title_to_update.items():
            try:
                book = Book.query.filter_by(title=b_title).first()
                if book:
                    book.title = b_new_title
                    db.session.flush()  # force to call hook "after_flush"
                    db.session.commit()
                    print(f"Updated Book: {book.to_dict()}")
            except (sqlalchemy.exc.IntegrityError, sqlite3.IntegrityError) as sqle:
                print(sqle)
                db.session.rollback()
            except Exception as e:
                db.session.rollback()
                print('Exception raised ..')
                print(e)

        # Restore the original function
        db.session.commit = original_commit

    @staticmethod
    def raise_interface_error():
        """
        Monkey-patching the db.session commit to raise sqlalchemy.exc.InterfaceError

        https://en.wikipedia.org/wiki/Monkey_patch

        Exception raised for errors that are related to the database interface
        rather than the database itself.
        This error is a DBAPI Error and originates from the database driver (DBAPI),
        not SQLAlchemy itself.
        The InterfaceError is sometimes raised by drivers in the context of the
        database connection being dropped, or not being able to connect to the database.
        """

        book_map_title_to_update = {
            'Cippalippa A': 'Book Heroes',
        }

        original_commit = db.session.commit

        def failing_commit():
            raise sqlalchemy.exc.InterfaceError(
                "Emulated InterfaceError during commit",
                params=dict(),
                orig=None)

        db.session.commit = failing_commit

        for b_title, b_new_title in book_map_title_to_update.items():
            try:
                book = Book.query.filter_by(title=b_title).first()
                if book:
                    book.title = b_new_title
                    db.session.commit()
                    print(f"Updated Book: {book.to_dict()}")
            except (sqlalchemy.exc.IntegrityError, sqlalchemy.exc.InterfaceError) as sqle:
                print(sqle)
                db.session.rollback()
            except Exception as e:
                db.session.rollback()
                print('Exception raised ..')
                print(e)

        # Restore the original commit method
        db.session.commit = original_commit

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
                    db.session.refresh(book)
                    print(f"Updated Book: {book.to_dict()}")
            except Exception as e:
                print(e)
                db.session.rollback()

    @staticmethod
    def list_all():
        books = Book.query.all()
        click.echo('Books:')
        for book in books:
            click.echo(book.to_dict())

        click.echo('+++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        authors = Author.query.all()
        click.echo('Authors:')
        for author in authors:
            click.echo(author.to_dict())

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
    def update_books_titles_with_IntegrityError_command():
        DatabaseCommands.update_books_titles_with_IntegrityError()

    @staticmethod
    @click.command('test-2')
    @with_appcontext
    def update_books_authors_with_IntegrityError_command():
        DatabaseCommands.update_books_author_with_IntegrityError()

    @staticmethod
    @click.command('test-3')
    @with_appcontext
    def raise_operational_db_error_command():
        DatabaseCommands.raise_operational_db_error()

    @staticmethod
    @click.command('test-4')
    @with_appcontext
    def raise_interface_error_command():
        DatabaseCommands.raise_interface_error()
    

    # @staticmethod
    # @click.command('test-2')
    # @with_appcontext
    # def update_books_with_exception_command():
    #     DatabaseCommands.update_books_with_exception()

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
        cli_commands = (
            cls.init_db_command,
            cls.clear_db_command,
            cls.reset_db_command,
            cls.add_sample_books_command,
            cls.update_books_titles_with_IntegrityError_command,
            cls.update_books_authors_with_IntegrityError_command,
            cls.raise_operational_db_error_command,
            cls.raise_interface_error_command,
            cls.list_all_command,
            cls.update_book,
            cls.create_book
        )

        for cmd in cli_commands:
            app.cli.add_command(cmd)

def init_app(app):
    DatabaseCommands.register_commands(app)