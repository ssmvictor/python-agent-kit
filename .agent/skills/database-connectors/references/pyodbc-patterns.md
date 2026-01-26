# pyodbc Patterns

> ODBC database connectivity patterns for enterprise environments.

---

## 1. Connection Patterns

### Connection String Builder

```python
from dataclasses import dataclass
from enum import Enum


class ODBCDriver(str, Enum):
    """Common ODBC drivers."""
    SQL_SERVER_17 = "ODBC Driver 17 for SQL Server"
    SQL_SERVER_18 = "ODBC Driver 18 for SQL Server"
    ACCESS = "Microsoft Access Driver (*.mdb, *.accdb)"
    MYSQL = "MySQL ODBC 8.0 Unicode Driver"


@dataclass
class ODBCConnectionString:
    """ODBC connection string builder."""
    driver: ODBCDriver
    server: str
    database: str
    username: str | None = None
    password: str | None = None
    trusted_connection: bool = False
    port: int | None = None
    timeout: int = 30
    encrypt: bool = True
    trust_server_cert: bool = False
    
    def build(self) -> str:
        parts = [f"DRIVER={{{self.driver.value}}}"]
        
        server = self.server
        if self.port:
            server = f"{self.server},{self.port}"
        parts.append(f"SERVER={server}")
        
        parts.append(f"DATABASE={self.database}")
        
        if self.trusted_connection:
            parts.append("Trusted_Connection=yes")
        else:
            parts.append(f"UID={self.username}")
            parts.append(f"PWD={self.password}")
        
        parts.append(f"Connection Timeout={self.timeout}")
        
        if self.encrypt:
            parts.append("Encrypt=yes")
        
        if self.trust_server_cert:
            parts.append("TrustServerCertificate=yes")
        
        return ";".join(parts)


# Usage:
conn_str = ODBCConnectionString(
    driver=ODBCDriver.SQL_SERVER_17,
    server="sqlserver.company.com",
    database="production",
    trusted_connection=True
).build()
```

---

## 2. Connection Manager

```python
from contextlib import contextmanager
from typing import Generator, List, Dict, Any, Optional
import pyodbc
import logging

logger = logging.getLogger(__name__)


class ODBCConnectionManager:
    """Manage ODBC connections with proper lifecycle."""
    
    def __init__(
        self,
        connection_string: str,
        autocommit: bool = False
    ) -> None:
        self._conn_str = connection_string
        self._autocommit = autocommit
    
    @contextmanager
    def connect(self) -> Generator[pyodbc.Connection, None, None]:
        """Get connection with automatic cleanup."""
        conn = pyodbc.connect(self._conn_str, autocommit=self._autocommit)
        try:
            yield conn
        except Exception:
            conn.rollback()
            raise
        else:
            if not self._autocommit:
                conn.commit()
        finally:
            conn.close()
    
    @contextmanager
    def cursor(self) -> Generator[pyodbc.Cursor, None, None]:
        """Get cursor with automatic cleanup."""
        with self.connect() as conn:
            cursor = conn.cursor()
            try:
                yield cursor
            finally:
                cursor.close()


# Usage:
manager = ODBCConnectionManager(conn_str)

with manager.cursor() as cursor:
    cursor.execute("SELECT * FROM users WHERE active = ?", (True,))
    rows = cursor.fetchall()
```

---

## 3. Query Executor

```python
from typing import List, Dict, Any, Tuple, Optional


class QueryExecutor:
    """Execute queries with proper typing."""
    
    def __init__(self, connection: pyodbc.Connection) -> None:
        self._conn = connection
    
    def execute(
        self,
        query: str,
        params: Tuple = ()
    ) -> int:
        """Execute non-select query, return rows affected."""
        cursor = self._conn.cursor()
        try:
            cursor.execute(query, params)
            return cursor.rowcount
        finally:
            cursor.close()
    
    def fetch_all(
        self,
        query: str,
        params: Tuple = ()
    ) -> List[Dict[str, Any]]:
        """Fetch all rows as dictionaries."""
        cursor = self._conn.cursor()
        try:
            cursor.execute(query, params)
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        finally:
            cursor.close()
    
    def fetch_one(
        self,
        query: str,
        params: Tuple = ()
    ) -> Optional[Dict[str, Any]]:
        """Fetch single row as dictionary."""
        cursor = self._conn.cursor()
        try:
            cursor.execute(query, params)
            row = cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))
            return None
        finally:
            cursor.close()
    
    def fetch_scalar(
        self,
        query: str,
        params: Tuple = ()
    ) -> Any:
        """Fetch single value."""
        cursor = self._conn.cursor()
        try:
            cursor.execute(query, params)
            row = cursor.fetchone()
            return row[0] if row else None
        finally:
            cursor.close()
    
    def execute_many(
        self,
        query: str,
        param_list: List[Tuple]
    ) -> int:
        """Execute query with multiple parameter sets."""
        cursor = self._conn.cursor()
        try:
            cursor.executemany(query, param_list)
            return cursor.rowcount
        finally:
            cursor.close()


# Usage:
with manager.connect() as conn:
    executor = QueryExecutor(conn)
    
    # Fetch all
    users = executor.fetch_all(
        "SELECT id, name, email FROM users WHERE department = ?",
        ("IT",)
    )
    
    # Fetch one
    user = executor.fetch_one(
        "SELECT * FROM users WHERE id = ?",
        (123,)
    )
    
    # Execute
    affected = executor.execute(
        "UPDATE users SET last_login = GETDATE() WHERE id = ?",
        (123,)
    )
```

---

## 4. Bulk Operations

```python
import csv
from pathlib import Path
from typing import List, Any


class BulkOperations:
    """Bulk insert/update operations."""
    
    def __init__(self, connection: pyodbc.Connection) -> None:
        self._conn = connection
    
    def bulk_insert(
        self,
        table: str,
        columns: List[str],
        data: List[List[Any]],
        batch_size: int = 1000
    ) -> int:
        """Insert data in batches."""
        if not data:
            return 0
        
        placeholders = ", ".join(["?" for _ in columns])
        column_list = ", ".join(columns)
        query = f"INSERT INTO {table} ({column_list}) VALUES ({placeholders})"
        
        cursor = self._conn.cursor()
        cursor.fast_executemany = True  # Enable fast executemany
        
        total_inserted = 0
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            cursor.executemany(query, batch)
            total_inserted += len(batch)
            self._conn.commit()
        
        return total_inserted
    
    def bulk_insert_from_csv(
        self,
        table: str,
        csv_path: Path,
        batch_size: int = 1000,
        skip_header: bool = True
    ) -> int:
        """Insert data from CSV file."""
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            
            if skip_header:
                columns = next(reader)
            else:
                # Read first row to determine columns
                first_row = next(reader)
                columns = [f"col{i}" for i in range(len(first_row))]
            
            data = list(reader)
        
        return self.bulk_insert(table, columns, data, batch_size)


# Usage:
with manager.connect() as conn:
    bulk = BulkOperations(conn)
    
    # From list
    rows_inserted = bulk.bulk_insert(
        "users",
        ["name", "email", "department"],
        [
            ["John Doe", "john@example.com", "IT"],
            ["Jane Smith", "jane@example.com", "HR"],
        ]
    )
    
    # From CSV
    rows_inserted = bulk.bulk_insert_from_csv(
        "import_data",
        Path("data.csv")
    )
```

---

## 5. Stored Procedures

```python
from typing import Any, Dict, List, Tuple


class StoredProcedureExecutor:
    """Execute stored procedures."""
    
    def __init__(self, connection: pyodbc.Connection) -> None:
        self._conn = connection
    
    def execute(
        self,
        proc_name: str,
        params: Tuple = ()
    ) -> List[Dict[str, Any]]:
        """Execute stored procedure and return results."""
        cursor = self._conn.cursor()
        try:
            cursor.execute(f"EXEC {proc_name} {', '.join(['?'] * len(params))}", params)
            
            if cursor.description:
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
            return []
        finally:
            cursor.close()
    
    def execute_with_output(
        self,
        proc_name: str,
        input_params: Dict[str, Any],
        output_params: List[str]
    ) -> Dict[str, Any]:
        """Execute procedure with output parameters."""
        cursor = self._conn.cursor()
        
        # Build parameter string
        param_parts = []
        values = []
        
        for name, value in input_params.items():
            param_parts.append(f"@{name} = ?")
            values.append(value)
        
        for name in output_params:
            param_parts.append(f"@{name} = ? OUTPUT")
            values.append(None)
        
        query = f"EXEC {proc_name} {', '.join(param_parts)}"
        cursor.execute(query, values)
        
        # Fetch output values (implementation depends on SQL Server version)
        return {}


# Usage:
with manager.connect() as conn:
    sp_executor = StoredProcedureExecutor(conn)
    
    results = sp_executor.execute(
        "sp_GetUsersByDepartment",
        ("IT",)
    )
```

---

## 6. Transaction Management

```python
from contextlib import contextmanager
from typing import Generator


class TransactionManager:
    """Explicit transaction management."""
    
    def __init__(self, connection: pyodbc.Connection) -> None:
        self._conn = connection
    
    @contextmanager
    def transaction(self) -> Generator[pyodbc.Cursor, None, None]:
        """Execute operations in a transaction."""
        cursor = self._conn.cursor()
        try:
            yield cursor
            self._conn.commit()
        except Exception:
            self._conn.rollback()
            raise
        finally:
            cursor.close()


# Usage:
with manager.connect() as conn:
    tx = TransactionManager(conn)
    
    with tx.transaction() as cursor:
        cursor.execute("INSERT INTO orders (...) VALUES (...)")
        cursor.execute("INSERT INTO order_items (...) VALUES (...)")
        cursor.execute("UPDATE inventory SET quantity = quantity - 1 WHERE ...")
        # All committed together, or all rolled back
```

---

> **Remember**: Always use parameterized queries, manage connections properly, and handle transactions explicitly.
