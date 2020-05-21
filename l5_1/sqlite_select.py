
import sqlite3

connection = sqlite3.connect('business.db')

cursor = connection.cursor()

product_cursor = cursor.execute('SELECT prodname, weight FROM products')
product_list = product_cursor.fetchall()

for product in product_list:
    print(product)