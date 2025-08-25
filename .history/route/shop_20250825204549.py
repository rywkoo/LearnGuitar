from flask import render_template
import sqlite3

from app import app  # assuming your Flask app is in app.py

@app.route('/shop')
def shop():
    # Connect to SQLite
    connection = sqlite3.connect('su79_database.sqlite3')
    cursor = connection.cursor()
    result = cursor.execute('SELECT * FROM products').fetchall()

    products = []  # create a list
    for row in result:
        products.append({
            'id': row[0],
            'title': row[1],
            'category': row[2],
            'price': row[3],
            'image': row[4],
        })
    
    # Pass products to template
    return render_template('shop.html', products=products)
