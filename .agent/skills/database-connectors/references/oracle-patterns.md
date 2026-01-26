# Oracle Patterns

> Oracle database connectivity with oracledb (cx_Oracle successor).

---

## 1. Connection Setup

### Configuration

```python
from dataclasses import dataclass
from typing import Optional


@dataclass
class OracleConfig:
    """Oracle database configuration."""
    host: str
    port: int
    service_name: str
    username: str
    password: str
    encoding: str = "UTF-8"
    min_connections: int = 2
    max_connections: int = 10
    
    @property
    def dsn(self) -> str:
        """Get DSN string."""
        return f"{self.host}:{self.port}/{self.service_name}"
    
    @property
    def connection_string(self) -> str:
        """Get full connection string."""
        return f"{self.username}/{self.password}@{self.dsn}"
```

### Connection Manager

```python
from contextlib import contextmanager
from typing import Generator, Any
import oracledb


class OracleConnectionManager:
    """Manage Oracle connections."""
    
    def __init__(self, config: OracleConfig) -> None:
        self._config = config
        self._pool: Optional[oracledb.ConnectionPool] = None
    
    def _ensure_pool(self) -> oracledb.ConnectionPool:
        """Create connection pool if not exists."""
        if self._pool is None:
            self._pool = oracledb.create_pool(
                user=self._config.username,
                password=self._config.password,
                dsn=self._config.dsn,
                min=self._config.min_connections,
                max=self._config.max_connections,
                encoding=self._config.encoding
            )
        return self._pool
    
    @contextmanager
    def connection(self) -> Generator[oracledb.Connection, None, None]:
        """Get pooled connection."""
        pool = self._ensure_pool()
        conn = pool.acquire()
        try:
            yield conn
        finally:
            pool.release(conn)
    
    @contextmanager
    def cursor(self) -> Generator[oracledb.Cursor, None, None]:
        """Get cursor with connection."""
        with self.connection() as conn:
            cursor = conn.cursor()
            try:
                yield cursor
            finally:
                cursor.close()
    
    def close(self) -> None:
        """Close connection pool."""
        if self._pool:
            self._pool.close()
            self._pool = None


# Usage:
config = OracleConfig(
    host="oracle.company.com",
    port=1521,
    service_name="PROD",
    username="app_user",
    password="secret"
)

manager = OracleConnectionManager(config)

with manager.cursor() as cursor:
    cursor.execute("SELECT * FROM employees WHERE department_id = :dept_id", {"dept_id": 10})
    rows = cursor.fetchall()
```

---

## 2. Query Execution

### Named Bindings

```python
from typing import Dict, Any, List, Optional


class OracleQueryExecutor:
    """Execute Oracle queries with named bindings."""
    
    def __init__(self, connection: oracledb.Connection) -> None:
        self._conn = connection
    
    def execute(
        self,
        query: str,
        params: Dict[str, Any] = None
    ) -> int:
        """Execute non-select query."""
        cursor = self._conn.cursor()
        try:
            cursor.execute(query, params or {})
            return cursor.rowcount
        finally:
            cursor.close()
    
    def fetch_all(
        self,
        query: str,
        params: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Fetch all rows as dictionaries."""
        cursor = self._conn.cursor()
        try:
            cursor.execute(query, params or {})
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        finally:
            cursor.close()
    
    def fetch_one(
        self,
        query: str,
        params: Dict[str, Any] = None
    ) -> Optional[Dict[str, Any]]:
        """Fetch single row."""
        cursor = self._conn.cursor()
        try:
            cursor.execute(query, params or {})
            row = cursor.fetchone()
            if row:
                columns = [col[0] for col in cursor.description]
                return dict(zip(columns, row))
            return None
        finally:
            cursor.close()


# Usage (Oracle uses :name bindings):
with manager.connection() as conn:
    executor = OracleQueryExecutor(conn)
    
    employees = executor.fetch_all(
        """
        SELECT employee_id, first_name, last_name, salary
        FROM employees
        WHERE department_id = :dept_id
        AND salary > :min_salary
        """,
        {"dept_id": 10, "min_salary": 50000}
    )
```

---

## 3. PL/SQL Execution

### Stored Procedures

```python
from typing import Any, Dict, List, Tuple


class PLSQLExecutor:
    """Execute PL/SQL procedures and functions."""
    
    def __init__(self, connection: oracledb.Connection) -> None:
        self._conn = connection
    
    def call_procedure(
        self,
        proc_name: str,
        params: List[Any] = None
    ) -> None:
        """Call stored procedure."""
        cursor = self._conn.cursor()
        try:
            cursor.callproc(proc_name, params or [])
        finally:
            cursor.close()
    
    def call_function(
        self,
        func_name: str,
        return_type: Any,
        params: List[Any] = None
    ) -> Any:
        """Call stored function and return result."""
        cursor = self._conn.cursor()
        try:
            result = cursor.callfunc(func_name, return_type, params or [])
            return result
        finally:
            cursor.close()
    
    def call_procedure_with_output(
        self,
        proc_name: str,
        in_params: Dict[str, Any],
        out_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Call procedure with output parameters."""
        cursor = self._conn.cursor()
        
        try:
            # Create output variables
            out_vars = {
                name: cursor.var(dtype)
                for name, dtype in out_params.items()
            }
            
            # Build parameter list
            all_params = {**in_params, **out_vars}
            
            # Build PL/SQL block
            param_list = ", ".join(f":{name}" for name in all_params.keys())
            plsql = f"BEGIN {proc_name}({param_list}); END;"
            
            cursor.execute(plsql, all_params)
            
            # Get output values
            return {name: var.getvalue() for name, var in out_vars.items()}
        finally:
            cursor.close()


# Usage:
with manager.connection() as conn:
    plsql = PLSQLExecutor(conn)
    
    # Call procedure
    plsql.call_procedure("update_employee_salary", [101, 5000])
    
    # Call function
    total = plsql.call_function(
        "get_department_total",
        oracledb.NUMBER,
        [10]
    )
    
    # Procedure with output
    result = plsql.call_procedure_with_output(
        "calculate_bonus",
        {"p_employee_id": 101, "p_percentage": 10},
        {"p_bonus": oracledb.NUMBER, "p_message": oracledb.STRING}
    )
```

---

## 4. LOB Handling

### CLOB and BLOB Operations

```python
from pathlib import Path


class LOBHandler:
    """Handle Oracle LOB (Large Object) types."""
    
    def __init__(self, connection: oracledb.Connection) -> None:
        self._conn = connection
    
    def write_clob(
        self,
        table: str,
        clob_column: str,
        key_column: str,
        key_value: Any,
        content: str
    ) -> None:
        """Write CLOB data."""
        cursor = self._conn.cursor()
        try:
            cursor.execute(
                f"UPDATE {table} SET {clob_column} = :content WHERE {key_column} = :key",
                {"content": content, "key": key_value}
            )
            self._conn.commit()
        finally:
            cursor.close()
    
    def read_clob(
        self,
        table: str,
        clob_column: str,
        key_column: str,
        key_value: Any
    ) -> str:
        """Read CLOB data."""
        cursor = self._conn.cursor()
        try:
            cursor.execute(
                f"SELECT {clob_column} FROM {table} WHERE {key_column} = :key",
                {"key": key_value}
            )
            row = cursor.fetchone()
            if row and row[0]:
                return row[0].read()
            return ""
        finally:
            cursor.close()
    
    def write_blob_from_file(
        self,
        table: str,
        blob_column: str,
        key_column: str,
        key_value: Any,
        file_path: Path
    ) -> None:
        """Write file to BLOB."""
        cursor = self._conn.cursor()
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            cursor.execute(
                f"UPDATE {table} SET {blob_column} = :content WHERE {key_column} = :key",
                {"content": content, "key": key_value}
            )
            self._conn.commit()
        finally:
            cursor.close()
    
    def read_blob_to_file(
        self,
        table: str,
        blob_column: str,
        key_column: str,
        key_value: Any,
        output_path: Path
    ) -> None:
        """Read BLOB to file."""
        cursor = self._conn.cursor()
        try:
            cursor.execute(
                f"SELECT {blob_column} FROM {table} WHERE {key_column} = :key",
                {"key": key_value}
            )
            row = cursor.fetchone()
            if row and row[0]:
                with open(output_path, 'wb') as f:
                    f.write(row[0].read())
        finally:
            cursor.close()
```

---

## 5. Batch Operations

```python
class OracleBatchOperations:
    """Batch insert/update operations."""
    
    def __init__(self, connection: oracledb.Connection) -> None:
        self._conn = connection
    
    def batch_insert(
        self,
        table: str,
        columns: List[str],
        data: List[List[Any]],
        batch_size: int = 1000
    ) -> int:
        """Insert data in batches using executemany."""
        if not data:
            return 0
        
        placeholders = ", ".join([f":{i+1}" for i in range(len(columns))])
        column_list = ", ".join(columns)
        query = f"INSERT INTO {table} ({column_list}) VALUES ({placeholders})"
        
        cursor = self._conn.cursor()
        cursor.setinputsizes(None, None)  # Auto-size
        
        total = 0
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            cursor.executemany(query, batch)
            total += len(batch)
            self._conn.commit()
        
        return total
    
    def merge(
        self,
        target_table: str,
        source_data: List[Dict[str, Any]],
        key_columns: List[str],
        update_columns: List[str]
    ) -> int:
        """MERGE operation (upsert)."""
        if not source_data:
            return 0
        
        all_columns = list(source_data[0].keys())
        
        # Build MERGE statement
        merge_sql = f"""
        MERGE INTO {target_table} t
        USING (SELECT {', '.join(f':{col} AS {col}' for col in all_columns)} FROM dual) s
        ON ({' AND '.join(f't.{col} = s.{col}' for col in key_columns)})
        WHEN MATCHED THEN UPDATE SET {', '.join(f't.{col} = s.{col}' for col in update_columns)}
        WHEN NOT MATCHED THEN INSERT ({', '.join(all_columns)}) VALUES ({', '.join(f's.{col}' for col in all_columns)})
        """
        
        cursor = self._conn.cursor()
        cursor.executemany(merge_sql, source_data)
        affected = cursor.rowcount
        self._conn.commit()
        
        return affected
```

---

> **Remember**: Oracle uses `:name` binding syntax. Always use connection pooling and proper LOB handling for large objects.
