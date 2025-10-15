"""
Library Service Module - Business Logic Functions
Contains all the core business logic for the Library Management System
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from database import (
    get_book_by_id, get_book_by_isbn, get_patron_borrow_count,
    insert_book, insert_borrow_record, update_book_availability,
    update_borrow_record_return_date, get_all_books, get_patron_borrowed_books, get_db_connection
)

def add_book_to_catalog(title: str, author: str, isbn: str, total_copies: int) -> Tuple[bool, str]:
    """
    Add a new book to the catalog.
    Implements R1: Book Catalog Management
    
    Args:
        title: Book title (max 200 chars)
        author: Book author (max 100 chars)
        isbn: 13-digit ISBN
        total_copies: Number of copies (positive integer)
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Input validation
    if not title or not title.strip():
        return False, "Title is required."
    
    if len(title.strip()) > 200:
        return False, "Title must be less than 200 characters."
    
    if not author or not author.strip():
        return False, "Author is required."
    
    if len(author.strip()) > 100:
        return False, "Author must be less than 100 characters."
    
    if len(isbn) != 13:
        return False, "ISBN must be exactly 13 digits."
    
    if not isinstance(total_copies, int) or total_copies <= 0:
        return False, "Total copies must be a positive integer."
    
    # Check for duplicate ISBN
    existing = get_book_by_isbn(isbn)
    if existing:
        return False, "A book with this ISBN already exists."
    
    # Insert new book
    success = insert_book(title.strip(), author.strip(), isbn, total_copies, total_copies)
    if success:
        return True, f'Book "{title.strip()}" has been successfully added to the catalog.'
    else:
        return False, "Database error occurred while adding the book."

def borrow_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    """
    Allow a patron to borrow a book.
    Implements R3 as per requirements  
    
    Args:
        patron_id: 6-digit library card ID
        book_id: ID of the book to borrow
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits."
    
    # Check if book exists and is available
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found."
    
    if book['available_copies'] <= 0:
        return False, "This book is currently not available."
    
    # Check patron's current borrowed books count
    current_borrowed = get_patron_borrow_count(patron_id)
    
    if current_borrowed > 5:
        return False, "You have reached the maximum borrowing limit of 5 books."
    
    # Create borrow record
    borrow_date = datetime.now()
    due_date = borrow_date + timedelta(days=14)
    
    # Insert borrow record and update availability
    borrow_success = insert_borrow_record(patron_id, book_id, borrow_date, due_date)
    if not borrow_success:
        return False, "Database error occurred while creating borrow record."
    
    availability_success = update_book_availability(book_id, -1)
    if not availability_success:
        return False, "Database error occurred while updating book availability."
    
    return True, f'Successfully borrowed "{book["title"]}". Due date: {due_date.strftime("%Y-%m-%d")}.'

def return_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    """
    Process book return by a patron.
    
    TODO: Implement R4 as per requirements
    - Accepts patron ID and book ID as form parameters
- Verifies the book was borrowed by the patron
- Updates available copies and records return date
- Calculates and displays any late fees owed
    """
    books = get_patron_borrowed_books(patron_id)
    if books == []:
        return False, "Patron not found or no books borrowed"
    book = []
    for book_borrowed in books:
        if book_borrowed['book_id'] == book_id:
            book = book_borrowed
            break
    if not book:
        return False, "Book not borrowed"
    fees = calculate_late_fee_for_book(patron_id, book_id)

    book_avail_updated = update_book_availability(book_id, 1)
    if not book_avail_updated:
        return False, "Book availability not updated"
    book_return = update_borrow_record_return_date(patron_id, book_id, datetime.now())
    if not book_return:
        return False, "Return date not updated"
    
    return True, "Successfully returned. Late fees: " + f"{fees['fee_amount']}"

def calculate_late_fee_for_book(patron_id: str, book_id: int) -> Dict:
    # Calculate late fees for a specific book.
    
    # TODO: Implement R5 as per requirements 
    books = get_patron_borrowed_books(patron_id)
    if (books == []):
        return { 
        'fee_amount': 0.00,
        'days_overdue': 0,
        'status': 'Patron not found or book not found'
    }
    for book_borrowed in books:
        if book_borrowed['book_id'] == book_id:
            book = book_borrowed
            break
    due_date = book['due_date']
    current_date = datetime.now()
    days_overdue = max((current_date - due_date).days, 0)

    if days_overdue <= 0:
        fee_amount = 0.00
    elif days_overdue <= 7:
        fee_amount = days_overdue * 0.50
    else:
        fee_amount = min(15.00, 7*0.50 + (days_overdue - 7)*1.00)
    
    return { 
        'fee_amount': fee_amount,
        'days_overdue': days_overdue,
        'status': 'Success'
    }


def search_books_in_catalog(search_term: str, search_type: str) -> List[Dict]:
    """
    Search for books in the catalog.
    The system shall provide search functionality with the following parameters:
- `q`: search term
- `type`: search type (title, author, isbn)
- Support partial matching for title/author (case-insensitive)
- Support exact matching for ISBN
- Return results in same format as catalog display
    
    TODO: Implement R6 as per requirements
    """
    if search_type == 'title':
        conn = get_db_connection()
        input = "SELECT * FROM books WHERE LOWER(title) LIKE ?"
        books = conn.execute(input, (f"%{search_term.lower()}%",)).fetchall()
        conn.close()
        if books:
            return [dict(book) for book in books]
    if search_type == 'isbn':
        book = get_book_by_isbn(search_term)
        if book:
            return [dict(book)]
    if search_type == 'author':
        conn = get_db_connection()
        input = "SELECT * FROM books WHERE LOWER(author) LIKE ?"
        books = conn.execute(input, (f"%{search_term.lower()}%",)).fetchall()
        conn.close()
        if books:
            return [dict(book) for book in books]
    return []

def get_patron_status_report(patron_id: str) -> Dict:
    """
    Get status report for a patron.
    The system shall display patron status for a particular patron that includes the following: 

- Currently borrowed books with due dates
- Total late fees owed  
- Number of books currently borrowed
- Borrowing history
    
    TODO: Implement R7 as per requirements
    """

    current_books = get_patron_borrowed_books(patron_id)
    total_books_out = get_patron_borrow_count(patron_id)
    conn = get_db_connection()
    records = conn.execute('''
        SELECT br.*, b.title, b.author 
        FROM borrow_records br 
        JOIN books b ON br.book_id = b.id 
        WHERE br.patron_id = ?
        ORDER BY br.borrow_date
    ''', (patron_id,)).fetchall()
    conn.close()

    if (current_books == [] and records == []):
        return {
        'borrowed_books': [],
        'total_late_fees': 0.00,
        'total_books_borrowed': 0,
        'borrowing_history': [],
        'status': "Patron not found"
        }
    if (current_books == []):
        return {
        'borrowed_books': [],
        'total_late_fees': 0.00,
        'total_books_borrowed': 0,
        'borrowing_history': records,
        'status': "Success"
        }

    total_fees = 0.00
    borrowed_books = []
    for book in current_books:
        borrowed_books.append({
            'book_id': book['book_id'],
            'title': book['title'],
            'author': book['author'],
            'due_date': datetime.fromisoformat(book['due_date']),
        })
        result = calculate_late_fee_for_book(patron_id, book['book_id'])
        late_fee = result['fee_amount']
        total_fees = total_fees + late_fee

    return {
        'borrowed_books': current_books,
        'total_late_fees': total_fees,
        'total_books_borrowed': total_books_out,
        'borrowing_history': records,
        'status': "Success"
    }
