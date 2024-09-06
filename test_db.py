import sqlite3

conn = sqlite3.connect('test.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS items
                  (name TEXT, quantity INTEGER)''')
cursor.execute("INSERT INTO items (name, quantity) VALUES (?, ?)",
               ("Тестовый товар", 100))
conn.commit()
cursor.execute("SELECT * FROM items")
rows = cursor.fetchall()
for row in rows:
    print(row)

conn.close()
