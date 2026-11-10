"""Deterministic report and optional AI-generated commentary."""
import os
from pathlib import Path

def make_report(db):
    s = db.stats()
    lines = [
        "DEAL RADAR v1.0 — аналитический отчёт",
        "Источник: учебные данные (не реальные предложения магазинов).",
        f"Товаров: {s['count']}",
        f"Средняя цена: {s['average']} ₸",
        f"Минимальная цена: {s['minimum']} ₸",
        f"Максимальная цена: {s['maximum']} ₸",
        "",
        "Средние цены по магазинам:"
    ]
    lines += [f"- {r['store']}: {r['average']} ₸ ({r['count']} шт.)"
              for r in db.by_store()]
    lines += ["", "Топ падений цены между двумя последними замерами:"]
    discounts = db.top_discounts()
    lines += [f"- {r['name']} ({r['store']}): {r['old_price']} → "
              f"{r['new_price']} ₸ (-{r['drop_pct']}%)" for r in discounts]
    if not discounts:
        lines.append("- Падений цены не обнаружено")
    lines += ["", "Примечание: снижение цены не гарантирует выгодную покупку."]
    return "\n".join(lines)

def ai_report(statistics):
    """Optional OpenAI API; does not run without key and installed openai package."""
    if not os.getenv("OPENAI_API_KEY"):
        return None
    try:
        from openai import OpenAI
    except ImportError:
        raise RuntimeError("Установите пакет: pip install openai")
    client = OpenAI()
    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        instructions=("Ты осторожный аналитик цен. Используй ТОЛЬКО предоставленные "
                      "цифры. Отметь, что это учебные данные, а не реальные скидки. "
                      "Не выдумывай факты. Ответ на русском: 3–5 предложений."),
        input=statistics,
    )
    return response.output_text

def save_report(text, path="reports/report.txt"):
    dest = Path(path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(text, encoding="utf-8")
    return dest
