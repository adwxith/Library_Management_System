import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, g
from datetime import date, timedelta
from datetime import timedelta

app = Flask(__name__)
app.config['DATABASE'] = {
    'host': 'localhost',
    'user': 'root',
    'password': 'ad123456',
    'database': 'library',
    'auth_plugin': 'mysql_native_password'
}






# Define a function to get the database connection
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = mysql.connector.connect(**app.config['DATABASE'], autocommit=True)
    return db





@app.route('/')
def index():
    return render_template('index.html')

# ... (previous imports and code) ...

@app.route('/members')
def members():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute('SELECT * FROM Members')
    members = cursor.fetchall()
    cursor.close()
    return render_template('members.html', members=members)



# ... (previous imports and code) ...



@app.route('/add_member', methods=['GET', 'POST'])
def add_member():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone_number = request.form['phone_number']
        
        cursor = get_db().cursor()
        cursor.execute('INSERT INTO Members (first_name, last_name, email, phone_number) VALUES (%s, %s, %s, %s)',
                       (first_name, last_name, email, phone_number))
        get_db().commit()  # Commit the changes directly on the database connection
        
        return redirect(url_for('members'))
    
    return render_template('add_member.html')


@app.route('/delete_member/<int:member_id>')
def delete_member(member_id):
    db = get_db()
    db.execute('DELETE FROM Members WHERE member_id = ?', (member_id,))
    db.commit()
    return redirect(url_for('members'))

# ... (previous imports and code) ...

@app.route('/books')
def books():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute('SELECT * FROM Books')
    books = cursor.fetchall()
    cursor.close()
    db.close()  # Close the database connection
    return render_template('books.html', books=books)




@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        publication_year = request.form['publication_year']
        isbn = request.form['isbn']
        total_copies = int(request.form['total_copies'])
        
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('INSERT INTO Books (title, author, publication_year, isbn, total_copies, available_copies) VALUES (%s, %s, %s, %s, %s, %s)',
                       (title, author, publication_year, isbn, total_copies, total_copies))
        db.commit()
        
        cursor.close()
        db.close()
        
        return redirect(url_for('books'))
    
    return render_template('add_book.html')


@app.route('/delete_book/<int:book_id>')
def delete_book(book_id):
    db, cursor = get_db()
    cursor.execute('DELETE FROM Books WHERE book_id = %s', (book_id,))
    db.commit()
    return redirect(url_for('books'))


@app.route('/renew', methods=['GET', 'POST'])
def renew():
    if request.method == 'POST':
        borrow_id = request.form['borrow_id']
        
        cursor = get_db().cursor(dictionary=True)  # Get the cursor directly
        
        cursor.execute('SELECT * FROM BorrowedBooks WHERE borrow_id = %s', (borrow_id,))
        borrowed_book = cursor.fetchone()

        if borrowed_book:
            return_date = borrowed_book[4]  # Assuming return_date is at index 4
            new_return_date = return_date + timedelta(days=7)  # Extend by 1 week
            cursor.execute('UPDATE BorrowedBooks SET return_date = %s WHERE borrow_id = %s', (new_return_date, borrow_id))
            cursor.close()  # Close the cursor
            db = get_db()
            db.commit()
            db.close()  # Close the database connection
            
            return render_template('renew_confirmation.html', borrow_id=borrow_id)

        else:
            error_message = "Invalid borrow ID."
            cursor.close()  # Close the cursor
            return render_template('renew_member.html', error_message=error_message)

    cursor = get_db().cursor()
    cursor.execute('SELECT borrow_id, member_id, book_id FROM BorrowedBooks')
    borrowed_books = cursor.fetchall()
    cursor.execute('SELECT member_id, first_name, last_name FROM Members')
    members = cursor.fetchall()
    cursor.close()  # Close the cursor
    
    return render_template('renew_member.html', members=members, borrowed_books=borrowed_books)


@app.route('/return_books', methods=['GET', 'POST'])
def return_books():
    if request.method == 'POST':
        member_id = request.form['member_id']
        book_id = request.form['book_id']

        db = get_db()
        cursor = db.cursor(dictionary=True)

        # Get the book's information before deleting the borrow record
        cursor.execute('SELECT Books.book_id, Books.total_copies FROM Books JOIN BorrowedBooks ON Books.book_id = BorrowedBooks.book_id WHERE BorrowedBooks.borrow_id = %s', (book_id,))
        book_info = cursor.fetchone()

        if book_info:
            # Update book availability
            cursor.execute('UPDATE Books SET available_copies = available_copies + 1 WHERE book_id = %s', (book_info['book_id'],))

            # Delete the borrow record for the specific book and member
            cursor.execute('DELETE FROM BorrowedBooks WHERE borrow_id = %s', (book_id,))

            # Update the total copies count since the book has been returned
            cursor.execute('UPDATE Books SET total_copies = total_copies + 1 WHERE book_id = %s', (book_info['book_id'],))

            db.commit()

            cursor.close()
            db.close()

            return redirect(url_for('index'))

    # This part handles GET requests to the /return_books route (displaying the form)
    # Fetch members and borrowed books for dropdowns
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute('SELECT DISTINCT Members.member_id, first_name, last_name FROM Members JOIN BorrowedBooks ON Members.member_id = BorrowedBooks.member_id')
    members = cursor.fetchall()
    cursor.execute('SELECT BorrowedBooks.borrow_id, Books.title FROM BorrowedBooks JOIN Books ON BorrowedBooks.book_id = Books.book_id')
    borrowed_books = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template('return_books.html', members=members, borrowed_books=borrowed_books)


@app.route('/borrowed_books')
def borrowed_books():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        SELECT Members.first_name, Members.last_name, Books.title, BorrowedBooks.borrow_date, BorrowedBooks.return_date
        FROM BorrowedBooks
        JOIN Members ON BorrowedBooks.member_id = Members.member_id
        JOIN Books ON BorrowedBooks.book_id = Books.book_id
    ''')
    borrowed_books = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('borrowed_books.html', borrowed_books=borrowed_books)




@app.route('/borrow', methods=['GET', 'POST'])
def borrow():
    if request.method == 'POST':
        member_id = request.form['member_id']
        book_id = request.form['book_id']

        db = get_db()  # Get the database connection
        cursor = db.cursor()  # Create a cursor object
        cursor.execute('SELECT * FROM Books WHERE book_id = %s', (book_id,))
        book = cursor.fetchone()

        if book and book[6] > 0:  # Check available_copies column index
            # Update book availability
            cursor.execute('UPDATE Books SET available_copies = available_copies - 1 WHERE book_id = %s', (book_id,))
            
            # Insert borrow record
            borrow_date = date.today()
            return_date = borrow_date + timedelta(days=14)  # Example: Borrow for 2 weeks
            cursor.execute('INSERT INTO BorrowedBooks (member_id, book_id, borrow_date, return_date) VALUES (%s, %s, %s, %s)',
                           (member_id, book_id, borrow_date, return_date))
            
            db.commit()
            
            return render_template('borrow_confirmation.html', member_id=member_id, book_id=book_id)

        else:
            error_message = "Book is not available for borrowing."
            members = cursor.execute('SELECT member_id, first_name, last_name FROM Members')
            books = cursor.execute('SELECT book_id, title FROM Books WHERE available_copies > 0')
            return render_template('select_member_to_borrow.html', error_message=error_message, members=members, books=books)

    # Fetch members and available books for dropdowns
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT member_id, first_name, last_name FROM Members')
    members = cursor.fetchall()
    cursor.execute('SELECT book_id, title FROM Books WHERE available_copies > 0')
    books = cursor.fetchall()

    return render_template('select_member_to_borrow.html', members=members, books=books)





if __name__ == '__main__':
    app.run(debug=True)
