import click
from flask.cli import with_appcontext
from .models import db, Book

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

@click.command('update-book')
@click.argument('id', type=int)
@click.argument('new_title')
@with_appcontext
def update_book(id, new_title):
    try:
        book = Book.query.get(id)
        if book:
            book.title = new_title
            db.session.commit()
            click.echo(f'Book with ID {id} updated to {new_title}.')
        else:
            click.echo(f'Book with ID {id} not found.')
    except Exception as e:
        click.echo(f'Error updating book: {e}')
        db.session.rollback()

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Initialize the database and populate it with sample data."""
    db.create_all()
    
    try:
        book1 = Book(title="Sample Book 1", author="Author Donald")
        book2 = Book(title="Sample Book 2", author="Author Duck")

        db.session.add(book1)
        db.session.add(book2)
        db.session.commit()

        click.echo("Database initialized and sample books added.")
    except Exception as e:
        print(e)
        db.session.rollback()

def init_app(app):
    app.cli.add_command(create_book)
    app.cli.add_command(update_book)
    app.cli.add_command(init_db_command)
