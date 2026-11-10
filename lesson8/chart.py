"""Create a line chart of product price history."""
from pathlib import Path

def save_chart(db, product_id, output="reports/price_chart.png"):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        raise RuntimeError("Установите matplotlib: pip install -r requirements.txt")
    rows = db.price_history(product_id)
    if not rows:
        raise ValueError("Нет истории для данного ID")
    dest = Path(output)
    dest.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(8, 4.5))
    plt.plot(range(1, len(rows)+1), [r["price"] for r in rows], marker="o")
    plt.xticks(range(1, len(rows)+1), [r["checked_at"][:10] for r in rows], rotation=25)
    plt.xlabel("Дата замера")
    plt.ylabel("Цена (KZT)")
    plt.title(f"История цены товара #{product_id}")
    plt.grid(alpha=0.25)
    plt.tight_layout()
    plt.savefig(dest, dpi=150)
    plt.close()
    return dest
