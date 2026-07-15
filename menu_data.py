MENU = {
    "ramen": {"label": "Ramen Tradizionale", "price": 120, "emoji": "🍜", "category": "🍲 Piatti Principali"},
    "sushi": {"label": "Set Sushi Variato", "price": 180, "emoji": "🍣", "category": "🍲 Piatti Principali"},
    "gyoza": {"label": "Gyoza alla Piastra (5 pz)", "price": 80, "emoji": "🥟", "category": "🍢 Snack & Sfizi"},
    "takoyaki": {"label": "Takoyaki Caldi", "price": 90, "emoji": "🐙", "category": "🍢 Snack & Sfizi"},
    "sake": {"label": "Sake Caldo", "price": 60, "emoji": "🍶", "category": "🍶 Bevande"},
    "birra": {"label": "Birra Sapporo alla Spina", "price": 50, "emoji": "🍺", "category": "🍶 Bevande"},
    "mochi": {"label": "Mochi al Tè Verde", "price": 40, "emoji": "🍡", "category": "🍡 Dolci"},
}

def get_item(key: str):
    return MENU.get(key.lower())