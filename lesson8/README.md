# Deal Radar v1.0 — полный проект к уроку 8

Учебная консольная программа на Python + SQLite: товары, магазины, история цен,
аналитика SQL, график matplotlib и опциональный отчёт через ChatGPT API.

**Данные демонстрационные**: цены, магазины и скидки вымышлены. Программа не делает
сетевой парсинг и не подтверждает реальную выгоду покупок.

## Быстрый старт

Нужен Python 3.10+.

```bash
python -m pip install -r requirements.txt
python main.py --demo
python main.py
```

Windows: если команда `python` не работает, попробуйте `py`.

В меню доступны поиск товаров дешевле N, топ-5 падений цены, статистика по
магазинам, график истории, импорт CSV и отчёт.

Быстрые команды:

```bash
python main.py --report
python main.py --chart 1
python main.py --import-csv data/new_prices_example.csv
python -m unittest discover -s tests -v
```

Файлы `deals.db`, `reports/report.txt`, `reports/price_chart.png` появляются после
запуска. График требует установленный matplotlib.

## Структура

- `database.py` — класс `Database`: `add_product`, `find_cheaper`, `price_history`,
  `stats`, `by_store`, `top_discounts`.
- `main.py` — меню и импорт CSV.
- `seed.py` — 8 демонстрационных товаров с двумя датами измерений.
- `chart.py` — построение графика.
- `report.py` — `make_report` и необязательный `ai_report`.
- `sql/analytics.sql` — запросы для DB Browser for SQLite.
- `data/new_prices_example.csv` — пример обновления данных.
- `tests/` — автоматические тесты.
- `TASKS.md` — задание студентам.

## Архитектура базы

`stores(id, name)` ← `products(id, name, store_id, price, rating, url)` ←
`price_history(id, product_id, price, checked_at)`.

URL уникален, поэтому обновление товара не создаёт дубль. Каждая загрузка
добавляет новое наблюдение цены. Топ скидок сравнивает **два последних замера**,
а не первую и последнюю цены за всё время. Для корректного вывода нужно как
минимум два замера. Снижение цены ≠ доказательство выгодной покупки.

При повторном `--demo` данные не дублируются. Для обновления используйте CSV
или вызов `Database.add_product()`.

## ИИ-отчёт

Без API-ключа: выберите пункт 6, откройте `reports/report.txt`, скопируйте его
в ChatGPT и попросите: «Сделай 5 предложений аналитики, опираясь только на
данные отчёта. Не выдумывай скидки и не называй это реальными предложениями».

С API:

```bash
python -m pip install openai
```

Установите `OPENAI_API_KEY` в переменную окружения (не в коде и не в Git).
Затем запустите `python main.py`, выберите 6 и ответьте `y`. Вызов API может
быть платным, требует доступа к выбранной модели и интернет-соединения.
При необходимости задайте `OPENAI_MODEL` доступной модели.

Не передавайте в ИИ персональные данные или секреты.

## GitHub и релиз

```bash
git init
git add .
git commit -m "Deal Radar v1.0"
git branch -M main
git remote add origin https://github.com/USER/REPO.git
git push -u origin main
git tag v1.0
git push origin v1.0
```

Замените USER/REPO на адрес своего созданного репозитория. На GitHub откройте
Releases → Draft a new release → выберите `v1.0`. В README добавьте свои
скриншоты меню, DB Browser, графика и отчёта.

## Связь с уроком 7

Урок 7 использовал таблицу `products` без `store_id`. Здесь новая расширенная
схема. Для начала рекомендуется новая база. Старую `deals.db` не перезаписывайте:
сделайте копию и при необходимости разработайте отдельную миграцию.
