-- Выполните эти запросы в DB Browser for SQLite (вкладка Execute SQL)
-- 1. Самый дешёвый товар
SELECT id, name, price FROM products ORDER BY price ASC, id ASC LIMIT 1;

-- 2. Топ-5 по рейтингу
SELECT name, rating, price FROM products ORDER BY rating DESC, price ASC LIMIT 5;

-- 3. Поиск по слову (LIKE в SQLite не различает регистр только для латиницы, поэтому два варианта написания)
SELECT name, price FROM products WHERE name LIKE '%Мышь%' OR name LIKE '%мыш%' ORDER BY name;

-- 4. Товары дешевле 20000
SELECT name, price FROM products WHERE price < 20000 ORDER BY price;

-- 5. Проверка дубликатов по URL
SELECT url, COUNT(*) AS total FROM products GROUP BY url HAVING COUNT(*) > 1;

-- Дополнительно: обновление и удаление (сначала убедитесь, что id существует)
-- UPDATE products SET price = 9990 WHERE id = 2;
-- DELETE FROM products WHERE id = 2;
