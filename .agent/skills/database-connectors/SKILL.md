---
name: database-connectors
description: Database connectivity principles. pyodbc, oracledb, pymssql, connection pooling, retry patterns for enterprise databases.
tier: standard
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Database Connectors Skill

> Database connectivity principles for enterprise environments.
> **OOP-first, strongly-typed, production-ready.**

---

## ⚠️ How to Use This Skill

This skill teaches **decision-making principles** for database connectivity, not fixed code to copy.

- ASK about target database before choosing driver
- Always use parameterized queries
- Implement connection pooling for production

---

## 1. Driver Selection (2025)

### Decision Tree

```
What database are you connecting to?
│
├── SQL Server
│   ├── pyodbc (preferred, ODBC driver)
│   └── pymssql (alternative, native)
│
├── Oracle
│   └── oracledb (recommended)
│
├── PostgreSQL
│   ├── psycopg2 (sync, most common)
│   └── asyncpg (async, high-performance)
│
├── MySQL
│   ├── mysql-connector-python (official)
│   └── pymysql (pure Python)
│
└── Multiple / ORM
    └── SQLAlchemy 2.0 (universal)
```

### Connection String Patterns

| Database | Format |
|----------|--------|
| SQL Server (pyodbc) | `DRIVER={ODBC Driver 17};SERVER=host;DATABASE=db;UID=user;PWD=pass` |
| Oracle | `user/pass@host:port/service` |
| PostgreSQL | `postgresql://user:pass@host:port/db` |
| MySQL | `mysql://user:pass@host:port/db` |

---

## 2. Connection Patterns

### Base Connection Manager

```python
from abc import ABC, abstractmethod
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Generator, TypeVar, Generic
import logging

logger = logging.getLogger(__name__)

Config = TypeVar('Config')
Connection = TypeVar('Connection')


@dataclass
class BaseDBConfig:
    """Base database configuration."""
    host: str
    port: int
    database: str
    username: str
    password: str
    timeout: int = 30
    
    @property
    @abstractmethod
    def connection_string(self) -> str:
        """Build connection string."""
        ...


class BaseConnectionManager(ABC, Generic[Config, Connection]):
    """Abstract connection manager."""
    
    def __init__(self, config: Config) -> None:
        self._config = config
        self._logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def connect(self) -> Connection:
        """Create a new connection."""
        ...
    
    @abstractmethod
    def close(self, conn: Connection) -> None:
        """Close a connection."""
        ...
    
    @abstractmethod
    def is_connected(self, conn: Connection) -> bool:
        """Check if connection is alive."""
        ...
    
    @contextmanager
    def connection(self) -> Generator[Connection, None, None]:
        """Context manager for connection lifecycle."""
        conn = self.connect()
        try:
            yield conn
        finally:
            self.close(conn)
```

### SQL Server Connection

```python
from dataclasses import dataclass
import pyodbc


@dataclass
class SQLServerConfig(BaseDBConfig):
    driver: str = "ODBC Driver 17 for SQL Server"
    trusted_connection: bool = False
    
    @property
    def connection_string(self) -> str:
        if self.trusted_connection:
            return (
                f"DRIVER={{{self.driver}}};"
                f"SERVER={self.host},{self.port};"
                f"DATABASE={self.database};"
                f"Trusted_Connection=yes;"
                f"Connection Timeout={self.timeout};"
            )
        return (
            f"DRIVER={{{self.driver}}};"
            f"SERVER={self.host},{self.port};"
            f"DATABASE={self.database};"
            f"UID={self.username};"
            f"PWD={self.password};"
            f"Connection Timeout={self.timeout};"
        )


class SQLServerManager(BaseConnectionManager[SQLServerConfig, pyodbc.Connection]):
    """SQL Server connection manager."""
    
    def connect(self) -> pyodbc.Connection:
        self._logger.debug(f"Connecting to {self._config.host}")
        return pyodbc.connect(self._config.connection_string)
    
    def close(self, conn: pyodbc.Connection) -> None:
        conn.close()
    
    def is_connected(self, conn: pyodbc.Connection) -> bool:
        try:
            conn.execute("SELECT 1")
            return True
        except Exception:
            return False


# Usage:
config = SQLServerConfig(
    host="sqlserver.company.com",
    port=1433,
    database="production",
    username="app_user",
    password="secret"
)

manager = SQLServerManager(config)
with manager.connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE active = ?", (True,))
    rows = cursor.fetchall()
```

### Oracle Connection

```python
from dataclasses import dataclass
import oracledb


@dataclass
class OracleConfig(BaseDBConfig):
    service_name: str = ""
    
    @property
    def connection_string(self) -> str:
        return f"{self.host}:{self.port}/{self.service_name or self.database}"


class OracleManager(BaseConnectionManager[OracleConfig, oracledb.Connection]):
    """Oracle connection manager."""
    
    def connect(self) -> oracledb.Connection:
        return oracledb.connect(
            user=self._config.username,
            password=self._config.password,
            dsn=self._config.connection_string
        )
    
    def close(self, conn: oracledb.Connection) -> None:
        conn.close()
    
    def is_connected(self, conn: oracledb.Connection) -> bool:
        try:
            conn.ping()
            return True
        except Exception:
            return False
```

---

## 3. Connection Pooling

### SQLAlchemy Pool

```python
from contextlib import contextmanager
from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.pool import QueuePool
from sqlalchemy.orm import Session, sessionmaker


class ConnectionPool:
    """SQLAlchemy-based connection pool."""
    
    def __init__(
        self,
        connection_url: str,
        pool_size: int = 5,
        max_overflow: int = 10,
        pool_timeout: int = 30,
        pool_recycle: int = 3600
    ) -> None:
        self._engine: Engine = create_engine(
            connection_url,
            poolclass=QueuePool,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_timeout=pool_timeout,
            pool_recycle=pool_recycle,
            pool_pre_ping=True,  # Test connections before use
        )
        self._session_factory = sessionmaker(bind=self._engine)
    
    @property
    def engine(self) -> Engine:
        return self._engine
    
    def execute(self, query: str, params: dict | None = None) -> list:
        """Execute raw SQL query."""
        with self._engine.connect() as conn:
            result = conn.execute(text(query), params or {})
            return result.fetchall()
    
    @contextmanager
    def session(self) -> Generator[Session, None, None]:
        """Get a session with automatic commit/rollback."""
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def dispose(self) -> None:
        """Dispose of the connection pool."""
        self._engine.dispose()


# Usage:
pool = ConnectionPool(
    "mssql+pyodbc://user:pass@host/db?driver=ODBC+Driver+17+for+SQL+Server",
    pool_size=10,
    max_overflow=20
)

# Raw query
rows = pool.execute("SELECT * FROM users WHERE status = :status", {"status": "active"})

# Session context
with pool.session() as session:
    result = session.execute(text("UPDATE users SET last_login = NOW() WHERE id = :id"), {"id": 1})
```

---

## 4. Retry Patterns

### Retry Decorator

```python
from functools import wraps
from typing import Callable, TypeVar, Tuple, Type
import time
import logging

T = TypeVar('T')
logger = logging.getLogger(__name__)


def retry_on_db_error(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
) -> Callable:
    """Retry decorator for database operations."""
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_error = None
            current_delay = delay
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_error = e
                    logger.warning(
                        f"{func.__name__} attempt {attempt + 1}/{max_attempts} "
                        f"failed: {e}"
                    )
                    if attempt < max_attempts - 1:
                        time.sleep(current_delay)
                        current_delay *= backoff
            
            raise last_error
        
        return wrapper
    return decorator


# Usage:
class UserRepository:
    @retry_on_db_error(max_attempts=3, delay=1.0)
    def get_user(self, user_id: int) -> dict:
        with self._pool.session() as session:
            result = session.execute(
                text("SELECT * FROM users WHERE id = :id"),
                {"id": user_id}
            )
            return dict(result.fetchone())
```

---

## 5. Repository Pattern

### Generic Repository

```python
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional, Type
from dataclasses import dataclass
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete

T = TypeVar('T')
ID = TypeVar('ID')


class Repository(ABC, Generic[T, ID]):
    """Abstract repository interface."""
    
    @abstractmethod
    def get_by_id(self, id: ID) -> Optional[T]: ...
    
    @abstractmethod
    def get_all(self, limit: int = 100) -> List[T]: ...
    
    @abstractmethod
    def add(self, entity: T) -> T: ...
    
    @abstractmethod
    def update(self, entity: T) -> T: ...
    
    @abstractmethod
    def delete(self, id: ID) -> bool: ...


class SQLAlchemyRepository(Repository[T, ID], Generic[T, ID]):
    """SQLAlchemy-based repository."""
    
    def __init__(self, session: Session, model_class: Type[T]) -> None:
        self._session = session
        self._model = model_class
    
    def get_by_id(self, id: ID) -> Optional[T]:
        return self._session.get(self._model, id)
    
    def get_all(self, limit: int = 100) -> List[T]:
        stmt = select(self._model).limit(limit)
        return list(self._session.scalars(stmt))
    
    def add(self, entity: T) -> T:
        self._session.add(entity)
        self._session.flush()
        return entity
    
    def update(self, entity: T) -> T:
        self._session.merge(entity)
        self._session.flush()
        return entity
    
    def delete(self, id: ID) -> bool:
        entity = self.get_by_id(id)
        if entity:
            self._session.delete(entity)
            self._session.flush()
            return True
        return False
```

---

## 6. Query Builder

### Type-Safe Query Builder

```python
from dataclasses import dataclass, field
from typing import Any, List, Tuple


@dataclass
class QueryBuilder:
    """Simple SQL query builder."""
    
    _select: List[str] = field(default_factory=lambda: ["*"])
    _from: str = ""
    _where: List[Tuple[str, Any]] = field(default_factory=list)
    _order_by: List[str] = field(default_factory=list)
    _limit: int | None = None
    _offset: int | None = None
    
    def select(self, *columns: str) -> "QueryBuilder":
        self._select = list(columns)
        return self
    
    def from_table(self, table: str) -> "QueryBuilder":
        self._from = table
        return self
    
    def where(self, column: str, value: Any) -> "QueryBuilder":
        self._where.append((column, value))
        return self
    
    def order_by(self, *columns: str) -> "QueryBuilder":
        self._order_by.extend(columns)
        return self
    
    def limit(self, n: int) -> "QueryBuilder":
        self._limit = n
        return self
    
    def offset(self, n: int) -> "QueryBuilder":
        self._offset = n
        return self
    
    def build(self) -> Tuple[str, List[Any]]:
        """Build SQL string and parameters."""
        parts = [f"SELECT {', '.join(self._select)}"]
        parts.append(f"FROM {self._from}")
        
        params = []
        if self._where:
            conditions = []
            for col, val in self._where:
                conditions.append(f"{col} = ?")
                params.append(val)
            parts.append(f"WHERE {' AND '.join(conditions)}")
        
        if self._order_by:
            parts.append(f"ORDER BY {', '.join(self._order_by)}")
        
        if self._limit:
            parts.append(f"LIMIT {self._limit}")
        
        if self._offset:
            parts.append(f"OFFSET {self._offset}")
        
        return " ".join(parts), params


# Usage:
query, params = (
    QueryBuilder()
    .select("id", "name", "email")
    .from_table("users")
    .where("status", "active")
    .where("department", "IT")
    .order_by("name ASC")
    .limit(50)
    .build()
)
# query: "SELECT id, name, email FROM users WHERE status = ? AND department = ? ORDER BY name ASC LIMIT 50"
# params: ["active", "IT"]
```

---

## 📚 References

See detailed patterns in:
- [pyodbc-patterns.md](./references/pyodbc-patterns.md)
- [oracle-patterns.md](./references/oracle-patterns.md)
- [connection-pooling.md](./references/connection-pooling.md)

---

## ✅ Decision Checklist

Before implementing database connectivity:

- [ ] Chose driver based on database type?
- [ ] Using typed configuration dataclass?
- [ ] Parameterized queries only (no SQL injection)?
- [ ] Connection pooling for production?
- [ ] Retry logic for transient failures?
- [ ] Credentials secured (env vars/secrets)?
- [ ] Connection cleanup guaranteed?

---

> **Remember**: Database connections are limited resources. Use pools, close connections, and handle errors gracefully.
