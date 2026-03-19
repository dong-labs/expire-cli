"""数据库 Schema 管理"""

from dong.db import SchemaManager
from .connection import ExpireDatabase

SCHEMA_VERSION = "1.0.0"


class ExpireSchemaManager(SchemaManager):
    """到期咚 Schema 管理器"""

    def __init__(self):
        super().__init__(
            db_class=ExpireDatabase,
            current_version=SCHEMA_VERSION
        )

    def init_schema(self) -> None:
        self._create_expires_table()
        self._create_renewals_table()
        self._create_indexes()

    def _create_expires_table(self) -> None:
        with ExpireDatabase.get_cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS expires (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    category TEXT,
                    expire_date TEXT NOT NULL,
                    cost REAL,
                    currency TEXT DEFAULT 'CNY',
                    repeat TEXT,
                    remind_days TEXT DEFAULT '30,7,1',
                    status TEXT DEFAULT 'active',
                    note TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def _create_renewals_table(self) -> None:
        with ExpireDatabase.get_cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS renewals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    expire_id INTEGER NOT NULL,
                    old_date TEXT NOT NULL,
                    new_date TEXT NOT NULL,
                    cost REAL,
                    renewed_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (expire_id) REFERENCES expires(id)
                )
            """)

    def _create_indexes(self) -> None:
        with ExpireDatabase.get_cursor() as cur:
            cur.execute("CREATE INDEX IF NOT EXISTS idx_expires_date ON expires(expire_date)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_expires_category ON expires(category)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_expires_status ON expires(status)")


def init_database():
    """初始化数据库"""
    manager = ExpireSchemaManager()
    manager.init_schema()
    return {"message": "数据库初始化成功", "version": SCHEMA_VERSION}


def is_initialized() -> bool:
    """检查数据库是否已初始化"""
    db_path = ExpireDatabase.get_db_path()
    if not db_path.exists():
        return False

    with ExpireDatabase.get_cursor() as cur:
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='expires'")
        return cur.fetchone() is not None
