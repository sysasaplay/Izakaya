import sqlite3
from datetime import datetime

class IzakayaDB:
    def __init__(self, db_name="izakaya.db"):
        self.db_name = db_name
        self.GOD_MODES = [876853397746225162, 1363915831091921098]

    def _connect(self):
        return sqlite3.connect(self.db_name)

    def setup(self):
        with self._connect() as conn:
            cursor = conn.cursor()
            # Tabella Utenti
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    balance INTEGER DEFAULT 500,
                    last_daily TEXT
                )
            """)
            # Tabella Inventario (Zaino)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS inventory (
                    user_id INTEGER,
                    item_id TEXT,
                    item_name TEXT,
                    quantity INTEGER DEFAULT 0,
                    PRIMARY KEY (user_id, item_id)
                )
            """)
            conn.commit()

    async def get_balance(self, user_id: int) -> int:
        if user_id in self.GOD_MODES:
            return 9999999
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            if row is None:
                cursor.execute("INSERT INTO users (user_id, balance) VALUES (?, 500)", (user_id,))
                conn.commit()
                return 500
            return row[0]

    async def add_coins(self, user_id: int, amount: int):
        if user_id in self.GOD_MODES:
            return
        await self.get_balance(user_id)
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
            conn.commit()

    async def check_and_set_daily(self, user_id: int) -> bool:
        if user_id in self.GOD_MODES:
            return True
            
        today = datetime.now().strftime("%Y-%m-%d")
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT last_daily FROM users WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            
            if row is None:
                cursor.execute("INSERT INTO users (user_id, balance, last_daily) VALUES (?, 500, ?)", (user_id, today))
                conn.commit()
                return True
                
            if row[0] == today:
                return False
                
            cursor.execute("UPDATE users SET last_daily = ? WHERE user_id = ?", (today, user_id))
            conn.commit()
            return True

    async def buy_item(self, user_id: int, price: int) -> bool:
        # Se sei tu o Ally, l'acquisto passa istantaneamente senza scalare nulla
        if user_id in self.GOD_MODES:
            return True
            
        current_balance = await self.get_balance(user_id)
        if current_balance < price:
            return False
            
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (price, user_id))
            conn.commit()
        return True

    async def add_to_inventory(self, user_id: int, item_id: str, item_name: str):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?", (user_id, item_id))
            row = cursor.fetchone()
            if row is None:
                cursor.execute("INSERT INTO inventory (user_id, item_id, item_name, quantity) VALUES (?, ?, ?, 1)", (user_id, item_id, item_name))
            else:
                cursor.execute("UPDATE inventory SET quantity = quantity + 1 WHERE user_id = ? AND item_id = ?", (user_id, item_id))
            conn.commit()

    async def get_inventory(self, user_id: int) -> list:
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT item_id, item_name, quantity FROM inventory WHERE user_id = ? AND quantity > 0", (user_id,))
            return cursor.fetchall()

    async def remove_one_from_inventory(self, user_id: int, item_id: str) -> bool:
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?", (user_id, item_id))
            row = cursor.fetchone()
            if row is None or row[0] <= 0:
                return False
            
            if row[0] == 1:
                cursor.execute("DELETE FROM inventory WHERE user_id = ? AND item_id = ?", (user_id, item_id))
            else:
                cursor.execute("UPDATE inventory SET quantity = quantity - 1 WHERE user_id = ? AND item_id = ?", (user_id, item_id))
            conn.commit()
            return True