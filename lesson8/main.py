"""Deal Radar v1.0 CLI. Run: python main.py --demo, then python main.py"""
import argparse
import csv
from pathlib import Path
from database import Database
from seed import load_demo
from report import make_report, save_report, ai_report
from chart import save_chart

def show(rows):
    if not rows:
        print("Ничего не найдено.")
        return
    for row in rows:
        print(" | ".join(f"{key}: {row[key]}" for key in row.keys()))

def import_csv(db, filename):
    """CSV columns: name,store,price,rating,url. One price observation per row."""
    with open(filename, encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        expected = {"name", "store", "price", "rating", "url"}
        if not expected.issubset(reader.fieldnames or []):
            raise ValueError(f"Нужны столбцы: {', '.join(sorted(expected))}")
        count = 0
        for row in reader:
            db.add_product(row["name"], float(row["price"]),
                           float(row["rating"]), row["url"], row["store"])
            count += 1
    print(f"Обновлено {count} наблюдений.")

def menu(db):
    while True:
        print("\n=== DEAL RADAR v1.0 ===")
        print("1. Все товары  2. Дешевле N  3. Топ-5 снижений")
        print("4. Средняя цена и магазины  5. История и график")
        print("6. Отчёт  7. Импорт CSV  0. Выход")
        choice = input("Выбор: ").strip()
        try:
            if choice == "0":
                break
            elif choice == "1":
                show(db.list_products())
            elif choice == "2":
                amount = float(input("Максимальная цена, ₸: "))
                keyword = input("Слово в названии (можно пусто): ")
                show(db.find_cheaper(amount, keyword))
            elif choice == "3":
                show(db.top_discounts())
            elif choice == "4":
                print(dict(db.stats()))
                show(db.by_store())
            elif choice == "5":
                pid = int(input("ID товара: "))
                show(db.price_history(pid))
                print("График:", save_chart(db, pid))
            elif choice == "6":
                report = make_report(db)
                print(report)
                print("Сохранено:", save_report(report))
                if input("Запросить ИИ-отчёт через API? [y/N]: ").lower() == "y":
                    result = ai_report(report)
                    if result is None:
                        print("Ключ не задан. Скопируйте reports/report.txt в ChatGPT вручную.")
                    else:
                        print(result)
                        print("Сохранено:", save_report(result, "reports/ai_report.txt"))
            elif choice == "7":
                import_csv(db, input("Путь к CSV: ").strip())
            else:
                print("Неизвестный пункт.")
        except (ValueError, OSError, RuntimeError) as exc:
            print("Ошибка:", exc)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--demo", action="store_true", help="Загрузить учебные данные")
    parser.add_argument("--import-csv", metavar="FILE", help="Импорт CSV без меню")
    parser.add_argument("--report", action="store_true", help="Сохранить отчёт и выйти")
    parser.add_argument("--chart", type=int, metavar="ID", help="Создать график по ID")
    parser.add_argument("--db", default=str(Path(__file__).resolve().parent / "deals.db"))
    args = parser.parse_args()
    db = Database(args.db)
    try:
        if args.demo:
            load_demo(db)
        if args.import_csv:
            import_csv(db, args.import_csv)
        if args.report:
            print(save_report(make_report(db)))
        if args.chart is not None:
            print(save_chart(db, args.chart))
        if not any([args.demo, args.import_csv, args.report, args.chart is not None]):
            menu(db)
    finally:
        db.close()

if __name__ == "__main__":
    main()
