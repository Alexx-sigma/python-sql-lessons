"""SQLite storage and analytics for Deal Radar v1.0 (Python 3.10+)."""
import sqlite3
from pathlib import Path

DEFAULT_DB = Path(__file__).resolve().parent / "deals.db"

class Database:
    def __init__(self, path=DEFAULT_DB):
        self.path = str(path)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.executescript("""
        CREATE TABLE IF NOT EXISTS stores (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        );
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            store_id INTEGER NOT NULL REFERENCES stores(id),
            price REAL NOT NULL CHECK(price >= 0),
            rating REAL CHECK(rating BETWEEN 0 AND 5),
            url TEXT NOT NULL UNIQUE
        );
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY,
            product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
            price REAL NOT NULL CHECK(price >= 0),
            checked_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
        );
        CREATE INDEX IF NOT EXISTS idx_history_product
            ON price_history(product_id, checked_at, id);
        """)
        self.conn.commit()

    def close(self):
        self.conn.close()

    def add_product(self, name, price, rating, url, store="Demo Store", checked_at=None):
        """Insert or update product by URL; append price observation every refresh."""
        if price < 0 or not (0 <= rating <= 5):
            raise ValueError("Цена >= 0, рейтинг от 0 до 5")
        with self.conn:
            self.conn.execute("INSERT OR IGNORE INTO stores(name) VALUES (?)", (store,))
            store_id = self.conn.execute(
                "SELECT id FROM stores WHERE name=?", (store,)
            ).fetchone()["id"]
            self.conn.execute("""
                INSERT INTO products(name, store_id, price, rating, url)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(url) DO UPDATE SET
                  name=excluded.name, store_id=excluded.store_id,
                  price=excluded.price, rating=excluded.rating
            """, (name, store_id, price, rating, url))
            product_id = self.conn.execute(
                "SELECT id FROM products WHERE url=?", (url,)
            ).fetchone()["id"]
            if checked_at is None:
                self.conn.execute(
                    "INSERT INTO price_history(product_id, price) VALUES (?, ?)",
                    (product_id, price))
            else:
                self.conn.execute(
                    "INSERT INTO price_history(product_id, price, checked_at) VALUES (?, ?, ?)",
                    (product_id, price, checked_at))
        return product_id

    def find_cheaper(self, limit, keyword=""):
        rows = self.conn.execute("""
            SELECT p.id, p.name, s.name AS store, p.price, p.rating
            FROM products p JOIN stores s ON s.id=p.store_id
            WHERE p.price < ? ORDER BY p.price, p.id
        """, (limit,)).fetchall()
        # SQLite LIKE is case-insensitive for ASCII only by default.
        # Python casefold supports Cyrillic search in this beginner project.
        return [row for row in rows if keyword.casefold() in row["name"].casefold()]

    def price_history(self, product_id):
        return self.conn.execute("""
            SELECT price, checked_at FROM price_history
            WHERE product_id=? ORDER BY checked_at, id
        """, (product_id,)).fetchall()

    def stats(self):
        return self.conn.execute("""
            SELECT COUNT(*) AS count, ROUND(AVG(price),2) AS average,
                   MIN(price) AS minimum, MAX(price) AS maximum
            FROM products
        """).fetchone()

    def by_store(self):
        return self.conn.execute("""
            SELECT s.name AS store, COUNT(*) AS count,
                   ROUND(AVG(p.price),2) AS average
            FROM stores s JOIN products p ON p.store_id=s.id
            GROUP BY s.id ORDER BY average
        """).fetchall()

    def top_discounts(self, limit=5):
        """Compare the two most recent observations of each product."""
        return self.conn.execute("""
            WITH ranked AS (
                SELECT product_id, price, checked_at,
                       ROW_NUMBER() OVER (
                         PARTITION BY product_id
                         ORDER BY checked_at DESC, id DESC
                       ) AS rn
                FROM price_history
            )
            SELECT p.id, p.name, s.name AS store,
                   old.price AS old_price, new.price AS new_price,
                   ROUND((old.price-new.price)*100.0/old.price,2) AS drop_pct
            FROM ranked new
            JOIN ranked old ON old.product_id=new.product_id AND old.rn=2
            JOIN products p ON p.id=new.product_id
            JOIN stores s ON s.id=p.store_id
            WHERE new.rn=1 AND old.price>0 AND new.price<old.price
            ORDER BY drop_pct DESC, p.id LIMIT ?
        """, (limit,)).fetchall()

    def list_products(self):
        return self.conn.execute("""
            SELECT p.id,p.name,s.name AS store,p.price,p.rating
            FROM products p JOIN stores s ON s.id=p.store_id ORDER BY p.id
        """).fetchall()
