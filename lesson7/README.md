# Урок 7. Склад данных — SQLite + Python + SQL

## Что внутри
- `main.py` — готовое консольное приложение на стандартной библиотеке Python.
- `deals.db` — заполненная учебная база SQLite.
- `data/products.csv` — 10 строк товаров, включая повтор URL для демонстрации дедупликации.
- `sql/schema.sql` — создание таблицы.
- `sql/quest.sql` — пять SQL-запросов для DB Browser for SQLite.
- `TASKS.md` — задания и оценивание на 12 баллов.

## Требования
Python 3.10+; внешние библиотеки не требуются. Для просмотра БД установите DB Browser for SQLite.

## Запуск
Откройте терминал в папке проекта.

Windows:
```cmd
py main.py init
py main.py import
py main.py list
py main.py quest --max-price 20000 --keyword мышь
```

Linux/macOS:
```bash
python3 main.py init
python3 main.py import
python3 main.py list
python3 main.py quest --max-price 20000 --keyword мышь
```

Добавление товара:
```bash
python3 main.py add "USB кабель" 1990 4.5 "https://example.com/products/usb-cable"
```

Изменение цены и удаление (сначала сделайте копию deals.db):
```bash
python3 main.py update-price 2 7990
python3 main.py delete 2
```

## Открытие в DB Browser for SQLite
1. File → Open Database → выберите `deals.db`.
2. В Browse Data выберите таблицу `products`.
3. Во вкладке Execute SQL выполняйте по одному запросу из `sql/quest.sql`.
4. Для изменений через интерфейс нажмите Write Changes.

## SQL-инъекции и безопасность
**Неправильно:**
```python
query = f"SELECT * FROM products WHERE name = '{user_input}'"
```
Ввод пользователя становится частью SQL-кода. Например, апостроф в названии может сломать запрос, а специально составленный ввод — изменить его смысл.

**Правильно:**
```python
cursor.execute('SELECT * FROM products WHERE name = ?', (user_input,))
```
Значение передаётся отдельно от SQL-кода. Не формируйте SQL-условия из пользовательского ввода через f-строки.

## Как работают ключи и дубликаты
`id` — уникальный первичный ключ; `url TEXT UNIQUE` запрещает одинаковые URL. Импорт использует `INSERT OR IGNORE`: повторный URL не добавляется. Повторное выполнение импорта не увеличивает число товаров.

В реальном проекте можно выбрать другую стратегию уникальности (например, по ID товара на сайте). Не удаляйте записи по совпадению названия без проверки: разные товары могут иметь одинаковые названия.

## Результат
Заполненная `deals.db`, пять проверенных запросов, понимание `sqlite3.connect`, `cursor`, `execute`, `commit` (в `with connection:` транзакция подтверждается автоматически), параметров `?` и защиты от SQL-инъекций.
