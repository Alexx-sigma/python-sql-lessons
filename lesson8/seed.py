"""Offline sample data: two observations per product; no live scraping."""
from database import Database

ITEMS = [
    ("Ноутбук Atlas 14", "TechShop", 350000, 315000, 4.7, "demo://atlas14"),
    ("Мышь Aero", "TechShop", 12000, 9000, 4.5, "demo://mouse"),
    ("Клавиатура KeyPro", "GadgetCity", 25000, 22500, 4.6, "demo://keys"),
    ("Монитор Vision 27", "GadgetCity", 115000, 109000, 4.8, "demo://monitor"),
    ("Наушники SoundX", "AudioMall", 45000, 33750, 4.4, "demo://sound"),
    ("Колонка MiniBeat", "AudioMall", 18000, 18000, 4.1, "demo://speaker"),
    ("SSD Fast 1TB", "TechShop", 42000, 39900, 4.9, "demo://ssd"),
    ("Веб-камера Clear", "GadgetCity", 28000, 21000, 4.3, "demo://camera"),
]

def load_demo(db: Database):
    """Only seed a fresh database; prevents accidental fake history on reruns."""
    if db.stats()["count"]:
        print("База уже заполнена. Демоданные не перезаписаны.")
        return
    for name, store, old, new, rating, url in ITEMS:
        db.add_product(name, old, rating, url, store, "2026-11-01T12:00:00Z")
        db.add_product(name, new, rating, url, store, "2026-11-06T12:00:00Z")
    print(f"Загружено {len(ITEMS)} учебных товаров и по два замера цены.")
