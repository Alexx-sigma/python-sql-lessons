-- Запускать в DB Browser for SQLite после python main.py --demo
SELECT COUNT(*) AS total, ROUND(AVG(price), 2) AS avg_price,
       MIN(price) AS min_price, MAX(price) AS max_price FROM products;

SELECT s.name AS store, COUNT(*) AS products_count,
       ROUND(AVG(p.price), 2) AS average_price
FROM stores s JOIN products p ON p.store_id=s.id
GROUP BY s.id ORDER BY average_price;

SELECT p.name, s.name AS store, p.price
FROM products p JOIN stores s ON s.id=p.store_id
ORDER BY p.price ASC LIMIT 5;

-- Последние два замера: падения цен
WITH ranked AS (
  SELECT product_id, price, checked_at,
         ROW_NUMBER() OVER (
           PARTITION BY product_id ORDER BY checked_at DESC, id DESC
         ) AS rn
  FROM price_history
)
SELECT p.name, old.price AS before_price, new.price AS now_price,
       ROUND(100.0*(old.price-new.price)/old.price, 2) AS discount_pct
FROM ranked new
JOIN ranked old ON old.product_id=new.product_id AND old.rn=2
JOIN products p ON p.id=new.product_id
WHERE new.rn=1 AND old.price>0 AND new.price<old.price
ORDER BY discount_pct DESC LIMIT 5;
