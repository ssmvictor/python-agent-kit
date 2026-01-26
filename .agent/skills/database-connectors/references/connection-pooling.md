# Connection Pooling Patterns

> Database connection pooling for enterprise applications.

---

## 1. Why Connection Pooling?

```
Without Pooling:
├── Each request creates new connection (~100ms)
├── Connection overhead for each operation
├── Database max connections quickly exhausted
└── Poor scalability

With Pooling:
├── Connections reused from pool
├── Near-zero connection overhead
├── Controlled resource consumption
└── Better scalability and performance
```

---

## 2. SQLAlchemy Pool

### Basic Pool Setup

```python
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool, NullPool
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator


class DatabasePool:
    """SQLAlchemy-based connection pool."""
    
    def __init__(
        self,
        connection_url: str,
        pool_size: int = 5,
        max_overflow: int = 10,
        pool_timeout: int = 30,
        pool_recycle: int = 3600,
        pool_pre_ping: bool = True
    ) -> None:
        """
        Initialize connection pool.
        
        Args:
            connection_url: Database URL
            pool_size: Number of permanent connections
            max_overflow: Additional connections allowed
            pool_timeout: Seconds to wait for connection
            pool_recycle: Seconds before recycling connection
            pool_pre_ping: Test connection before use
        """
        self._engine = create_engine(
            connection_url,
            poolclass=QueuePool,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_timeout=pool_timeout,
            pool_recycle=pool_recycle,
            pool_pre_ping=pool_pre_ping,
        )
        self._session_factory = sessionmaker(bind=self._engine)
    
    @property
    def engine(self):
        return self._engine
    
    @contextmanager
    def session(self) -> Generator[Session, None, None]:
        """Get session with automatic commit/rollback."""
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    @contextmanager
    def connection(self):
        """Get raw connection."""
        conn = self._engine.connect()
        try:
            yield conn
        finally:
            conn.close()
    
    def execute(self, query: str, params: dict = None) -> list:
        """Execute query and return results."""
        with self.connection() as conn:
            result = conn.execute(text(query), params or {})
            return result.fetchall()
    
    def dispose(self) -> None:
        """Dispose of connection pool."""
        self._engine.dispose()
    
    def get_pool_status(self) -> dict:
        """Get pool statistics."""
        pool = self._engine.pool
        return {
            "size": pool.size(),
            "checkedin": pool.checkedin(),
            "checkedout": pool.checkedout(),
            "overflow": pool.overflow(),
        }


# Connection URLs for different databases:
"""
SQLServer: mssql+pyodbc://user:pass@host/db?driver=ODBC+Driver+17+for+SQL+Server
PostgreSQL: postgresql://user:pass@host:5432/db
MySQL: mysql+pymysql://user:pass@host:3306/db
Oracle: oracle+oracledb://user:pass@host:1521/?service_name=ORCL
SQLite: sqlite:///path/to/db.sqlite
"""
```

---

## 3. Pool Configuration by Use Case

### Configuration Profiles

```python
from dataclasses import dataclass
from enum import Enum


class PoolProfile(str, Enum):
    """Predefined pool profiles."""
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    HIGH_LOAD = "high_load"
    BATCH = "batch"


@dataclass
class PoolConfig:
    """Pool configuration."""
    pool_size: int
    max_overflow: int
    pool_timeout: int
    pool_recycle: int
    pool_pre_ping: bool
    
    @classmethod
    def for_profile(cls, profile: PoolProfile) -> "PoolConfig":
        """Get config for profile."""
        configs = {
            PoolProfile.DEVELOPMENT: cls(
                pool_size=2,
                max_overflow=3,
                pool_timeout=10,
                pool_recycle=300,
                pool_pre_ping=True
            ),
            PoolProfile.PRODUCTION: cls(
                pool_size=10,
                max_overflow=20,
                pool_timeout=30,
                pool_recycle=3600,
                pool_pre_ping=True
            ),
            PoolProfile.HIGH_LOAD: cls(
                pool_size=25,
                max_overflow=50,
                pool_timeout=60,
                pool_recycle=1800,
                pool_pre_ping=True
            ),
            PoolProfile.BATCH: cls(
                pool_size=5,
                max_overflow=10,
                pool_timeout=120,
                pool_recycle=7200,
                pool_pre_ping=False  # Batch jobs use dedicated connections
            ),
        }
        return configs[profile]


# Usage:
config = PoolConfig.for_profile(PoolProfile.PRODUCTION)

pool = DatabasePool(
    connection_url="postgresql://user:pass@host/db",
    pool_size=config.pool_size,
    max_overflow=config.max_overflow,
    pool_timeout=config.pool_timeout,
    pool_recycle=config.pool_recycle,
    pool_pre_ping=config.pool_pre_ping
)
```

---

## 4. Read/Write Splitting

### Primary/Replica Pattern

```python
from typing import Optional


class ReadWritePool:
    """Pool with read/write splitting."""
    
    def __init__(
        self,
        primary_url: str,
        replica_urls: list[str],
        **pool_kwargs
    ) -> None:
        self._primary = DatabasePool(primary_url, **pool_kwargs)
        self._replicas = [
            DatabasePool(url, **pool_kwargs)
            for url in replica_urls
        ]
        self._replica_index = 0
    
    def _get_next_replica(self) -> DatabasePool:
        """Round-robin replica selection."""
        if not self._replicas:
            return self._primary
        
        replica = self._replicas[self._replica_index]
        self._replica_index = (self._replica_index + 1) % len(self._replicas)
        return replica
    
    def write_session(self):
        """Get session for write operations."""
        return self._primary.session()
    
    def read_session(self):
        """Get session for read operations."""
        return self._get_next_replica().session()
    
    def dispose(self) -> None:
        """Dispose all pools."""
        self._primary.dispose()
        for replica in self._replicas:
            replica.dispose()


# Usage:
pool = ReadWritePool(
    primary_url="postgresql://user:pass@primary/db",
    replica_urls=[
        "postgresql://user:pass@replica1/db",
        "postgresql://user:pass@replica2/db",
    ],
    pool_size=10
)

# Write to primary
with pool.write_session() as session:
    session.execute(text("INSERT INTO users (name) VALUES (:name)"), {"name": "John"})

# Read from replica
with pool.read_session() as session:
    result = session.execute(text("SELECT * FROM users"))
```

---

## 5. Health Monitoring

### Pool Health Checker

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class PoolHealth:
    """Pool health status."""
    healthy: bool
    connections_available: int
    connections_in_use: int
    overflow_in_use: int
    last_check: datetime
    error_message: Optional[str] = None


class PoolHealthMonitor:
    """Monitor pool health."""
    
    def __init__(self, pool: DatabasePool) -> None:
        self._pool = pool
    
    def check_health(self) -> PoolHealth:
        """Check pool health."""
        try:
            # Test connection
            with self._pool.connection() as conn:
                conn.execute(text("SELECT 1"))
            
            status = self._pool.get_pool_status()
            
            return PoolHealth(
                healthy=True,
                connections_available=status["checkedin"],
                connections_in_use=status["checkedout"],
                overflow_in_use=status["overflow"],
                last_check=datetime.now()
            )
        except Exception as e:
            logger.error(f"Pool health check failed: {e}")
            return PoolHealth(
                healthy=False,
                connections_available=0,
                connections_in_use=0,
                overflow_in_use=0,
                last_check=datetime.now(),
                error_message=str(e)
            )
    
    def is_healthy(self) -> bool:
        """Quick health check."""
        return self.check_health().healthy


# Usage:
monitor = PoolHealthMonitor(pool)

health = monitor.check_health()
if not health.healthy:
    logger.critical(f"Database pool unhealthy: {health.error_message}")
```

---

## 6. Connection Cleanup

### Automatic Cleanup

```python
import atexit
import signal
from typing import List


class PoolManager:
    """Manage multiple connection pools with cleanup."""
    
    _pools: List[DatabasePool] = []
    
    @classmethod
    def register(cls, pool: DatabasePool) -> DatabasePool:
        """Register pool for automatic cleanup."""
        cls._pools.append(pool)
        return pool
    
    @classmethod
    def cleanup_all(cls) -> None:
        """Dispose all registered pools."""
        for pool in cls._pools:
            try:
                pool.dispose()
            except Exception as e:
                logger.error(f"Error disposing pool: {e}")
        cls._pools.clear()
    
    @classmethod
    def setup_signal_handlers(cls) -> None:
        """Setup handlers for graceful shutdown."""
        def handler(signum, frame):
            cls.cleanup_all()
        
        signal.signal(signal.SIGTERM, handler)
        signal.signal(signal.SIGINT, handler)
        atexit.register(cls.cleanup_all)


# Usage:
PoolManager.setup_signal_handlers()

pool = PoolManager.register(
    DatabasePool("postgresql://user:pass@host/db")
)

# Pools will be automatically cleaned up on exit
```

---

## 7. Multi-Database Pool

```python
from typing import Dict


class MultiDatabasePool:
    """Manage pools for multiple databases."""
    
    def __init__(self) -> None:
        self._pools: Dict[str, DatabasePool] = {}
    
    def add_database(
        self,
        name: str,
        connection_url: str,
        **pool_kwargs
    ) -> None:
        """Add database pool."""
        self._pools[name] = DatabasePool(connection_url, **pool_kwargs)
    
    def get(self, name: str) -> DatabasePool:
        """Get pool by name."""
        if name not in self._pools:
            raise KeyError(f"Database '{name}' not configured")
        return self._pools[name]
    
    def session(self, name: str):
        """Get session from named pool."""
        return self.get(name).session()
    
    def dispose_all(self) -> None:
        """Dispose all pools."""
        for pool in self._pools.values():
            pool.dispose()
        self._pools.clear()


# Usage:
pools = MultiDatabasePool()

pools.add_database("users", "postgresql://user:pass@users-db/users")
pools.add_database("orders", "postgresql://user:pass@orders-db/orders")

with pools.session("users") as session:
    users = session.execute(text("SELECT * FROM users"))

with pools.session("orders") as session:
    orders = session.execute(text("SELECT * FROM orders"))
```

---

> **Remember**: Size your pools based on expected load. Monitor pool health and set appropriate timeouts for your workload.
