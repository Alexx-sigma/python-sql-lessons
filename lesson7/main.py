"""Урок 7: учебный склад товаров на SQLite. Python 3.10+."""
import argparse
import csv
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / 'deals.db'
CSV_PATH = ROOT / 'data' / 'products.csv'
SCHEMA = '''
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price REAL NOT NULL CHECK(price >= 0),
    rating REAL CHECK(rating BETWEEN 0 AND 5),
    url TEXT NOT NULL UNIQUE
);
'''


def connect():
    return sqlite3.connect(DB_PATH)


def init_db():
    with connect() as connection:
        connection.execute(SCHEMA)
    print(f'База готова: {DB_PATH}')


def import_csv():
    init_db()
    with CSV_PATH.open('r', encoding='utf-8-sig', newline='') as file:
        rows = list(csv.DictReader(file))
    values = [(r['name'], float(r['price']), float(r['rating']), r['url']) for r in rows]
    with connect() as connection:
        before = connection.total_changes
        connection.executemany(
            'INSERT OR IGNORE INTO products (name, price, rating, url) VALUES (?, ?, ?, ?)',
            values,
        )
        added = connection.total_changes - before
    print(f'Прочитано строк CSV: {len(rows)}. Добавлено новых товаров: {added}.')


def show(query, params=()):
    with connect() as connection:
        cursor = connection.cursor()
        cursor.execute(query, params)
        result = cursor.fetchall()
        headers = [column[0] for column in cursor.description]
    print(' | '.join(headers))
    print('-' * 75)
    for row in result:
        print(' | '.join(str(value) for value in row))
    if not result:
        print('(нет результатов)')


def quest(max_price, keyword):
    init_db()
    tasks = [
        ('1. Самый дешёвый товар',
         'SELECT id, name, price FROM products ORDER BY price ASC, id ASC LIMIT 1', ()),
        ('2. Топ-5 по рейтингу',
         'SELECT name, rating, price FROM products ORDER BY rating DESC, price ASC LIMIT 5', ()),
        ('3. Поиск по слову',
         'SELECT name, price FROM products WHERE name LIKE ? ORDER BY name', (f'%{keyword}%',)),
        ('4. Товары дешевле N',
         'SELECT name, price FROM products WHERE price < ? ORDER BY price', (max_price,)),
        ('5. Поиск дубликатов по URL',
         'SELECT url, COUNT(*) AS count FROM products GROUP BY url HAVING COUNT(*) > 1', ()),
    ]
    for title, query, params in tasks:
        print(f'\n=== {title} ===')
        show(query, params)


def add_product(name, price, rating, url):
    init_db()
    try:
        with connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                'INSERT INTO products (name, price, rating, url) VALUES (?, ?, ?, ?)',
                (name, price, rating, url),
            )
            print(f'Товар добавлен, id={cursor.lastrowid}')
    except sqlite3.IntegrityError as error:
        print(f'Товар не добавлен: {error}')


def update_price(product_id, price):
    with connect() as connection:
        cursor = connection.cursor()
        cursor.execute('UPDATE products SET price = ? WHERE id = ?', (price, product_id))
        print(f'Обновлено записей: {cursor.rowcount}')


def delete_product(product_id):
    with connect() as connection:
        cursor = connection.cursor()
        cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
        print(f'Удалено записей: {cursor.rowcount}')


def main():
    parser = argparse.ArgumentParser(description='Учебная база товаров SQLite')
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('init', help='Создать таблицу')
    sub.add_parser('import', help='Импортировать CSV (повторы по URL игнорируются)')
    sub.add_parser('list', help='Показать все товары')
    quest_parser = sub.add_parser('quest', help='Выполнить 5 SQL-запросов')
    quest_parser.add_argument('--max-price', type=float, default=20000)
    quest_parser.add_argument('--keyword', default='Мышь')
    add = sub.add_parser('add', help='Добавить товар')
    add.add_argument('name')
    add.add_argument('price', type=float)
    add.add_argument('rating', type=float)
    add.add_argument('url')
    update = sub.add_parser('update-price', help='Изменить цену по id')
    update.add_argument('id', type=int)
    update.add_argument('price', type=float)
    delete = sub.add_parser('delete', help='Удалить товар по id')
    delete.add_argument('id', type=int)
    args = parser.parse_args()
    if args.command == 'init':
        init_db()
    elif args.command == 'import':
        import_csv()
    elif args.command == 'list':
        init_db()
        show('SELECT id, name, price, rating, url FROM products ORDER BY id')
    elif args.command == 'quest':
        quest(args.max_price, args.keyword)
    elif args.command == 'add':
        add_product(args.name, args.price, args.rating, args.url)
    elif args.command == 'update-price':
        update_price(args.id, args.price)
    elif args.command == 'delete':
        delete_product(args.id)


if __name__ == '__main__':
    main()
