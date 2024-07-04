import csv
from datetime import datetime
from sqlalchemy.orm import Session
from .celery_config import app
from database.connection import get_db
from database.models import Book, Borrow


@app.task(name="celery_tasks.save_report_to_csv")
def save_report_to_csv():
    print('Task started')
    db: Session = next(get_db())

    available_books = db.query(Book).filter(Book.quantity > 0).all()

    borrowed_books = db.query(Borrow).all()

    available_books_file = f'csv_report/available_books_{datetime.now().strftime("%Y_%m_%d")}.csv'
    borrowed_books_file = f'csv_report/borrowed_books_{datetime.now().strftime("%Y_%m_%d")}.csv'

    with open(available_books_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['ID', 'Title', 'Author ID', 'Category ID', 'Quantity'])
        for book in available_books:
            writer.writerow([book.id, book.title, book.author_id, book.category_id, book.quantity])

    with open(borrowed_books_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Borrow ID', 'Book ID', 'User ID', 'Borrow Date'])
        for borrow in borrowed_books:
            writer.writerow([borrow.id, borrow.book_id, borrow.user_id, borrow.borrow_date])

    print(f'Reports saved: {available_books_file}, {borrowed_books_file}')


save_report_to_csv.delay()

