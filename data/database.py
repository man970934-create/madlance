"""Работа с базой данных"""
import os
import aiosqlite
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from config import DATABASE_URL

DB_PATH = DATABASE_URL.replace("sqlite:///", "")

# Создаем директорию для БД, если её нет
db_dir = os.path.dirname(DB_PATH)
if db_dir and not os.path.exists(db_dir):
    os.makedirs(db_dir, exist_ok=True)


class Database:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path

    async def _connect(self):
        return await aiosqlite.connect(self.db_path)

    async def init_db(self):
        """Инициализация таблиц"""
        db = await self._connect()
        try:
            await db.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    telegram_id INTEGER UNIQUE NOT NULL,
                    username TEXT,
                    full_name TEXT,
                    role TEXT CHECK(role IN ('customer', 'executor', 'none')) DEFAULT 'none',
                    referrer_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (referrer_id) REFERENCES users(id)
                );

                CREATE TABLE IF NOT EXISTS subscriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    tariff TEXT NOT NULL,
                    start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    end_date TIMESTAMP NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                );

                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    channel TEXT
                );

                CREATE TABLE IF NOT EXISTS user_categories (
                    user_id INTEGER NOT NULL,
                    category_id INTEGER NOT NULL,
                    PRIMARY KEY (user_id, category_id),
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (category_id) REFERENCES categories(id)
                );

                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    category_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    budget TEXT,
                    deadline TEXT,
                    file_ids TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    message_id INTEGER,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (category_id) REFERENCES categories(id)
                );

                CREATE TABLE IF NOT EXISTS resumes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    category_id INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    message_id INTEGER,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (category_id) REFERENCES categories(id)
                );

                CREATE TABLE IF NOT EXISTS payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    type TEXT NOT NULL,
                    amount INTEGER NOT NULL,
                    payload TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                );

                CREATE TABLE IF NOT EXISTS referrals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    referrer_id INTEGER NOT NULL,
                    referred_id INTEGER NOT NULL UNIQUE,
                    bonus_applied BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (referrer_id) REFERENCES users(id),
                    FOREIGN KEY (referred_id) REFERENCES users(id)
                );
            """)
            await db.commit()
        finally:
            await db.close()

    async def get_or_create_user(self, telegram_id: int, username: str = None, full_name: str = None) -> Dict[str, Any]:
        db = await self._connect()
        try:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return dict(row)
                await db.execute(
                    "INSERT INTO users (telegram_id, username, full_name) VALUES (?, ?, ?)",
                    (telegram_id, username, full_name)
                )
                await db.commit()
                async with db.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)) as cursor:
                    return dict(await cursor.fetchone())
        finally:
            await db.close()

    async def set_user_role(self, user_id: int, role: str):
        db = await self._connect()
        try:
            await db.execute("UPDATE users SET role = ? WHERE id = ?", (role, user_id))
            await db.commit()
        finally:
            await db.close()

    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        db = await self._connect()
        try:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None
        finally:
            await db.close()

    async def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        db = await self._connect()
        try:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM users WHERE id = ?", (user_id,)) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None
        finally:
            await db.close()

    async def init_categories(self, categories: Dict[str, str]):
        db = await self._connect()
        try:
            for name, channel in categories.items():
                await db.execute(
                    "INSERT OR IGNORE INTO categories (name, channel) VALUES (?, ?)",
                    (name, channel)
                )
            await db.commit()
        finally:
            await db.close()

    async def get_categories(self) -> List[Dict[str, Any]]:
        db = await self._connect()
        try:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM categories") as cursor:
                return [dict(row) async for row in cursor]
        finally:
            await db.close()

    async def get_category_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        db = await self._connect()
        try:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM categories WHERE name = ?", (name,)) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None
        finally:
            await db.close()

    async def set_user_categories(self, user_id: int, category_ids: List[int]):
        db = await self._connect()
        try:
            await db.execute("DELETE FROM user_categories WHERE user_id = ?", (user_id,))
            for cid in category_ids:
                await db.execute(
                    "INSERT INTO user_categories (user_id, category_id) VALUES (?, ?)",
                    (user_id, cid)
                )
            await db.commit()
        finally:
            await db.close()

    async def get_user_categories(self, user_id: int) -> List[Dict[str, Any]]:
        db = await self._connect()
        try:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT c.* FROM categories c
                JOIN user_categories uc ON c.id = uc.category_id
                WHERE uc.user_id = ?
            """, (user_id,)) as cursor:
                return [dict(row) async for row in cursor]
        finally:
            await db.close()

    async def create_task(self, user_id: int, category_id: int, title: str, description: str,
                          budget: str = None, deadline: str = None, file_ids: str = None) -> int:
        expires_at = datetime.now() + timedelta(days=90)
        db = await self._connect()
        try:
            cursor = await db.execute(
                """INSERT INTO tasks (user_id, category_id, title, description, budget, deadline, file_ids, expires_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (user_id, category_id, title, description, budget, deadline, file_ids, expires_at.isoformat())
            )
            await db.commit()
            return cursor.lastrowid
        finally:
            await db.close()

    async def get_task(self, task_id: int) -> Optional[Dict[str, Any]]:
        db = await self._connect()
        try:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None
        finally:
            await db.close()

    async def update_task_message_id(self, task_id: int, message_id: int):
        db = await self._connect()
        try:
            await db.execute("UPDATE tasks SET message_id = ? WHERE id = ?", (message_id, task_id))
            await db.commit()
        finally:
            await db.close()

    async def archive_expired_tasks(self):
        db = await self._connect()
        try:
            await db.execute(
                "UPDATE tasks SET status = 'archived' WHERE status = 'active' AND expires_at < ?",
                (datetime.now().isoformat(),)
            )
            await db.commit()
        finally:
            await db.close()

    async def get_active_tasks_by_category(self, category_id: int) -> List[Dict[str, Any]]:
        db = await self._connect()
        try:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM tasks WHERE category_id = ? AND status = 'active'",
                (category_id,)
            ) as cursor:
                return [dict(row) async for row in cursor]
        finally:
            await db.close()

    async def create_resume(self, user_id: int, category_id: int, content: str) -> int:
        expires_at = datetime.now() + timedelta(days=90)
        db = await self._connect()
        try:
            cursor = await db.execute(
                "INSERT INTO resumes (user_id, category_id, content, expires_at) VALUES (?, ?, ?, ?)",
                (user_id, category_id, content, expires_at.isoformat())
            )
            await db.commit()
            return cursor.lastrowid
        finally:
            await db.close()

    async def update_resume_message_id(self, resume_id: int, message_id: int):
        db = await self._connect()
        try:
            await db.execute("UPDATE resumes SET message_id = ? WHERE id = ?", (message_id, resume_id))
            await db.commit()
        finally:
            await db.close()

    async def archive_expired_resumes(self):
        db = await self._connect()
        try:
            await db.execute(
                "UPDATE resumes SET status = 'archived' WHERE status = 'active' AND expires_at < ?",
                (datetime.now().isoformat(),)
            )
            await db.commit()
        finally:
            await db.close()

    async def create_payment(self, user_id: int, ptype: str, amount: int, payload: str) -> int:
        db = await self._connect()
        try:
            cursor = await db.execute(
                "INSERT INTO payments (user_id, type, amount, payload) VALUES (?, ?, ?, ?)",
                (user_id, ptype, amount, payload)
            )
            await db.commit()
            return cursor.lastrowid
        finally:
            await db.close()

    async def confirm_payment(self, payload: str):
        db = await self._connect()
        try:
            await db.execute("UPDATE payments SET status = 'paid' WHERE payload = ?", (payload,))
            await db.commit()
        finally:
            await db.close()

    async def get_payment_by_payload(self, payload: str) -> Optional[Dict[str, Any]]:
        db = await self._connect()
        try:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM payments WHERE payload = ?", (payload,)) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None
        finally:
            await db.close()

    async def create_subscription(self, user_id: int, tariff: str, days: int):
        start_date = datetime.now()
        end_date = start_date + timedelta(days=days)
        db = await self._connect()
        try:
            await db.execute(
                "INSERT INTO subscriptions (user_id, tariff, start_date, end_date) VALUES (?, ?, ?, ?)",
                (user_id, tariff, start_date.isoformat(), end_date.isoformat())
            )
            await db.commit()
        finally:
            await db.close()

    async def get_active_subscription(self, user_id: int) -> Optional[Dict[str, Any]]:
        db = await self._connect()
        try:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                """SELECT * FROM subscriptions 
                   WHERE user_id = ? AND is_active = 1 AND end_date > ?
                   ORDER BY end_date DESC LIMIT 1""",
                (user_id, datetime.now().isoformat())
            ) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None
        finally:
            await db.close()

    async def extend_subscription(self, user_id: int, hours: int):
        sub = await self.get_active_subscription(user_id)
        if sub:
            new_end = datetime.fromisoformat(sub["end_date"]) + timedelta(hours=hours)
            db = await self._connect()
            try:
                await db.execute(
                    "UPDATE subscriptions SET end_date = ? WHERE id = ?",
                    (new_end.isoformat(), sub["id"])
                )
                await db.commit()
            finally:
                await db.close()
        else:
            await self.create_subscription(user_id, "referral", hours / 24)

    async def add_referral(self, referrer_id: int, referred_id: int):
        db = await self._connect()
        try:
            await db.execute(
                "INSERT INTO referrals (referrer_id, referred_id) VALUES (?, ?)",
                (referrer_id, referred_id)
            )
            await db.commit()
        except aiosqlite.IntegrityError:
            pass  # Already referred
        finally:
            await db.close()

    async def apply_referral_bonus(self, referred_id: int):
        db = await self._connect()
        try:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM referrals WHERE referred_id = ? AND bonus_applied = 0",
                (referred_id,)
            ) as cursor:
                ref = await cursor.fetchone()
                if ref:
                    from config import REFERRAL_BONUS_HOURS
                    await self.extend_subscription(ref["referrer_id"], REFERRAL_BONUS_HOURS)
                    await db.execute(
                        "UPDATE referrals SET bonus_applied = 1 WHERE id = ?",
                        (ref["id"],)
                    )
                    await db.commit()
        finally:
            await db.close()

    async def get_stats(self) -> Dict[str, int]:
        db = await self._connect()
        try:
            stats = {}
            for table in ["users", "tasks", "resumes", "subscriptions", "payments"]:
                async with db.execute(f"SELECT COUNT(*) FROM {table}") as cursor:
                    stats[table] = (await cursor.fetchone())[0]
            return stats
        finally:
            await db.close()

    async def get_all_users(self) -> List[Dict[str, Any]]:
        db = await self._connect()
        try:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM users") as cursor:
                return [dict(row) async for row in cursor]
        finally:
            await db.close()


db = Database()
