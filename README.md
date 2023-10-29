# Library Management System

This is a basic implementation of a Library Management System using Flask, MySQL, plain HTML, and CSS. This system provides functionalities to view members, add members, view books and their quantities, add books, borrow books, return books, renew borrowed books, and view the details of who borrowed which book. As of now, there is no login system implemented.

## Prerequisites

Before running the system, make sure you have the following requirements installed on your machine:

- Python
- Flask
- MySQL
- MySQL Connector for Python
- HTML and CSS knowledge for customizing the front-end (if needed)

## Getting Started

1. Clone the repository to your local machine.
2. Set up your MySQL database with the name `library` and configure the connection details in the `app.config['DATABASE']` section in the `app.py` file.

```python
app.config['DATABASE'] = {
    'host': 'localhost',
    'user': 'root',
    'password': 'ad123456',
    'database': 'library',
    'auth_plugin': 'mysql_native_password'
}
```

3. Create the necessary database tables by running the SQL commands found in the `database.sql` file in your MySQL server.

4. Install the required Python packages:

```
pip install flask mysql-connector-python
```

5. Run the application:

```
python app.py
```

## Functionality

### Home Page

- Access the home page of the library management system.

### View Members

- Click on "View Members" to see a list of all the members in the library.

### Add Member

- Click on "Add Member" to add a new member to the library by filling in the member's details.

### View Books

- Click on "View Books" to see a list of all the available books in the library along with their quantities.

### Add Book

- Click on "Add Book" to add a new book to the library by providing book details and the total number of copies.

### Borrow Books

- Click on "Borrow Books" to initiate the borrowing process. You can select a member and an available book to borrow. The system will automatically update the available copies.

### Return Books

- Click on "Return Books" to return a borrowed book. You can select the member and the book to return, and the system will update the book's availability.

### Renew Borrowed Books

- Click on "Renew Borrowed Books" to renew a borrowed book. You can extend the return date for an additional week.

### Borrowed Books

- View the details of who borrowed which book, along with borrow and return dates.

## Customization

You can customize the front-end of the system by modifying the HTML and CSS files in the `templates` and `static` directories, respectively. Feel free to style and structure the system according to your preferences.

## Author

Adwaith Sajeev C

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
