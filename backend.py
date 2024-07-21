import sqlite3

def connect():
    conn = sqlite3.connect("library.db")
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS book (id INTEGER PRIMARY KEY, title TEXT, author TEXT, year INTEGER, isbn INTEGER, genre TEXT, availability INTEGER)")
    conn.commit()
    conn.close()

def insert(title, author, year, isbn, genre, availability):
    conn = sqlite3.connect("library.db")
    cur = conn.cursor()
    cur.execute("INSERT INTO book VALUES (NULL, ?, ?, ?, ?, ?, ?)", (title, author, year, isbn, genre, availability))
    conn.commit()
    conn.close()
    view()

def view():
    conn = sqlite3.connect("library.db")
    cur = conn.cursor()
    cur.execute("SELECT id, title, author, year, isbn, genre FROM book")
    rows = cur.fetchall()
    conn.close()
    return rows

def search(title="", author="", year="", isbn="", genre=""):
    conn = sqlite3.connect("library.db")
    cur = conn.cursor()

    query = "SELECT * FROM book WHERE 1=1"
    parameters = []

    if title:
        query += " AND title LIKE ?"
        parameters.append(title + '%')

    if author:
        query += " AND author LIKE ?"
        parameters.append(author + '%')

    if year:
        query += " AND year LIKE ?"
        parameters.append(year + '%')

    if isbn:
        query += " AND isbn LIKE ?"
        parameters.append(isbn + '%')

    if genre:
        genres = genre.split(",")
        genre_conditions = " AND ".join(["genre LIKE ?" for _ in genres])
        query += f" AND ({genre_conditions})"
        for genre_value in genres:
            parameters.append('%' + genre_value.strip() + '%')

    cur.execute(query, parameters)
    rows = cur.fetchall()
    conn.close()
    return rows

def delete(id):
    conn = sqlite3.connect("library.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM book WHERE id=?", (id,))
    conn.commit()
    conn.close()

def update(id, title, author, year, isbn, genre, availability):
    conn = sqlite3.connect("library.db")
    cur = conn.cursor()
    cur.execute("UPDATE book SET title=?, author=?, year=?, isbn=?, genre=?, availability=? WHERE id=?", (title, author, year, isbn, genre, availability, id))
    conn.commit()
    conn.close()

def get_availability(book_id):
    conn = sqlite3.connect("library.db")
    cur = conn.cursor()
    cur.execute("SELECT availability FROM book WHERE id=?", (book_id,))
    availability = cur.fetchone()[0]
    conn.close()
    return availability

    
connect()